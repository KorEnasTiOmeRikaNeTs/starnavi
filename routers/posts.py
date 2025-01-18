# routers/posts.py

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Posts, Status, Comments, Users
from database import get_db
from schemas import PostPutRequest
from ai_funcs import safety_check
from routers.auth import get_current_user


router = APIRouter(prefix="/posts", tags=["post"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("")
def get_posts(db: db_dependency):
    raw_result = (
        db.query(
            Posts.title,
            Posts.content,
            Posts.created_at,
            Users.username,
            Posts.id,
            func.count(Comments.id).label("comment_count"),
        )
        .outerjoin(Comments, Comments.post_id == Posts.id)
        .outerjoin(Users, Users.id == Posts.created_by)
        .filter(Posts.status == Status.POSTED)
        .group_by(
            Users.username,
            Posts.id,
            Posts.title,
            Posts.content,
            Posts.created_at,
        )
        .all()
    )

    result = [
        {
            "title": post[0],
            "content": post[1],
            "created_at": post[2],
            "created_by": post[3],
            "post_id": post[4],
            "comments_count": post[5],
        }
        for post in raw_result
    ]
    return result


@router.post("/create-post", status_code=status.HTTP_201_CREATED)
def create_post(user: user_dependency, db: db_dependency, post_request: PostPutRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    if safety_check(post_request.content):
        post_status = Status.POSTED
    else:
        post_status = Status.BLOCKED

    create_post_model = Posts(
        title=post_request.title,
        content=post_request.content,
        status=post_status,
        created_by=user.get("id"),
    )

    db.add(create_post_model)
    db.commit()


@router.put("/{post_id}/update-post")
def update_post(
    user: user_dependency, db: db_dependency, put_request: PostPutRequest, post_id: int
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post = (
        db.query(Posts)
        .filter(Posts.id == post_id)
        .filter(Posts.created_by == user.get("id"))
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if safety_check(put_request.content) is None:
        post_status = Status.POSTED
    else:
        post_status = Status.BLOCKED

    post.status = post_status

    if put_request.title is not None:
        post.title = put_request.title
    if put_request.content is not None:
        post.content = put_request.content

    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}/delete")
def delete_post(user: user_dependency, db: db_dependency, post_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    post = (
        db.query(Posts)
        .filter(Posts.id == post_id)
        .filter(Posts.created_by == user.get("id"))
        .first()
    )

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
