from typing import Literal

from datetime import datetime

from pydantic import BaseModel, Field


class AutoReplyStatusForm(BaseModel):
    status: Literal["on", "off"]
    timer: int = 5


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class PostPutRequest(BaseModel):
    title: str
    content: str


class CommentRequest(BaseModel):
    content: str


class CommentAnalytics(BaseModel):
    date: datetime
    created_comments: int
    blocked_comments: int
