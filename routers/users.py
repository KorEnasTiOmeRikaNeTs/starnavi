# routers/users.py

from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import Users, AutoReply, AutoReplyStatus
from database import get_db
from schemas import UserVerification, AutoReplyStatusForm
from routers.auth import get_current_user


router = APIRouter(prefix="/user", tags=["user"])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/profile-page", status_code=status.HTTP_200_OK)
def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = (
        db.query(Users)
        .join(AutoReply, AutoReply.user_id == Users.id)
        .filter(Users.id == user.get("id"))
        .first()
    )

    return {
        "id": user_model.id,
        "username": user_model.username,
        "email": user_model.email,
        "autoreply_status": (
            user_model.autoreply[0].status if user_model.autoreply else None
        ),
        "autoreply_timer": (
            user_model.autoreply[0].timer if user_model.autoreply else None
        ),
    }


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    user: user_dependency, db: db_dependency, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/change-autoreply", status_code=status.HTTP_204_NO_CONTENT)
def change_autoreply(
    user: user_dependency, db: db_dependency, autoreply_status: AutoReplyStatusForm
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_model = (
        db.query(Users)
        .join(AutoReply, AutoReply.user_id == Users.id)
        .filter(Users.id == user.get("id"))
        .first()
    )

    if autoreply_status.status == "on":
        user_model.autoreply[0].status = AutoReplyStatus.ON
    else:
        user_model.autoreply[0].status = AutoReplyStatus.OFF

    user_model.autoreply[0].timer = timedelta(minutes=autoreply_status.timer)

    db.add(user_model)
    db.commit()
