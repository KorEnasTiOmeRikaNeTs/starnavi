# routers/comments.py

from typing import Annotated
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy import func, cast, Date, event
from sqlalchemy.sql.expression import case
from sqlalchemy.orm import Session, sessionmaker, mapper

from models import Comments, Status, Users, Posts, AutoReply, AutoReplyStatus
from database import get_db, scheduler
from schemas import CommentRequest
from ai_funcs import safety_check, auto_comment_answer
from routers.auth import get_current_user


router = APIRouter(tags=["comments"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@event.listens_for(Comments, "after_insert")
def check_auto_reply(mapper, connection, target):

    with next(get_db()) as db:

        post = (
            db.query(Posts)
            .join(Users, Users.id == Posts.created_by)
            .filter(Posts.id == target.post_id)
            .first()
        )

        post_owner_id = post.user.id
        post_text = post.content
        comment_text = target.content

        if post_owner_id == target.created_by:
            print("auto reply does not work on itself")
            return False

        auto_reply_model = (
            db.query(AutoReply).filter(AutoReply.user_id == post_owner_id).first()
        )
        auto_reply_status = auto_reply_model.status == AutoReplyStatus.ON

    if auto_reply_status:
        scheduler.add_job(
            auto_reply,
            "date",
            run_date=datetime.now()
            + timedelta(seconds=auto_reply_model.timer.total_seconds()),
            args=(
                target.post_id,
                target.created_by,
                post_text,
                comment_text,
                post_owner_id,
            ),
        )


def auto_reply(post_id, comment_owner_id, post_text, comment_text, post_owner_id):

    with next(get_db()) as db:
        comment_owner = db.query(Users).filter(Users.id == comment_owner_id).first()
        comment_owner_name = comment_owner.username

        raw_reply = auto_comment_answer(post_text, comment_text)
        reply = f"Dear {comment_owner_name}, {raw_reply}"

        reply_model = Comments(
            content=reply,
            status=Status.POSTED,
            post_id=post_id,
            created_by=post_owner_id,
        )

        db.add(reply_model)
        db.commit()


@router.post(
    "/post/{post_id}/create-comments",
    operation_id="create_comment_for_post",
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    user: user_dependency,
    db: db_dependency,
    comment_request: CommentRequest,
    post_id: int,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is None:
        raise HTTPException(
            status_code=404, detail=f"post with post_id={post_id} does not exist"
        )

    try:
        if safety_check(comment_request.content):
            post_status = Status.POSTED
        else:
            post_status = Status.BLOCKED
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    create_comment_model = Comments(
        content=comment_request.content,
        status=post_status,
        post_id=post_id,
        created_by=user.get("id"),
    )

    db.add(create_comment_model)
    db.commit()


@router.get("/post/{post_id}/comments")
def comments_from_post(user: user_dependency, db: db_dependency, post_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    raw_result = (
        db.query(
            Users.username,
            Comments.content,
            Comments.created_at,
        )
        .outerjoin(Users, Users.id == Comments.created_by)
        .filter(Comments.status == Status.POSTED)
        .filter(Comments.post_id == post_id)
        .all()
    )

    result = [
        {
            "username": comment[0],
            "content": comment[1],
            "created_at": comment[2],
        }
        for comment in raw_result
    ]

    return result


@router.post("/post/{post_id}/create-comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    user: user_dependency,
    db: db_dependency,
    comment_request: CommentRequest,
    post_id: int,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post = db.query(Posts).filter(Posts.id == post_id).first()
    if post is None:
        raise HTTPException(
            status_code=404, detail=f"post with post_id={post_id} does not exist"
        )

    try:
        if safety_check(comment_request.content):
            post_status = Status.POSTED
        else:
            post_status = Status.BLOCKED
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    create_comment_model = Comments(
        content=comment_request.content,
        status=post_status,
        post_id=post_id,
        created_by=user.get("id"),
    )

    db.add(create_comment_model)
    db.commit()


@router.get("/comments-daily-breakdown")
def comment_daily_breakdown(
    user: user_dependency, db: db_dependency, date_from: date, date_to: date
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    if date_from > date_to:
        raise HTTPException(
            status_code=400, detail="date_from cannot be greater than date_to"
        )

    raw_result = (
        db.query(
            cast(Comments.created_at, Date),
            func.sum(case((Comments.status == Status.POSTED, 1), else_=0)),
            func.sum(case((Comments.status == Status.BLOCKED, 1), else_=0)),
        )
        .filter(Comments.created_at >= date_from, Comments.created_at <= date_to)
        .group_by(cast(Comments.created_at, Date))
        .all()
    )

    result = [
        {"date": result[0], "posted_comments": result[1], "blocked_comments": result[2]}
        for result in raw_result
    ]

    return result
