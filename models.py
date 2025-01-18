# models.py

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Interval, Enum, ForeignKey, func, Date
from sqlalchemy.orm import relationship

from enum import Enum as PyEnum


class Status(PyEnum):
    POSTED = "posted"
    BLOCKED = "blocked"


class AutoReplyStatus(PyEnum):
    ON = "on"
    OFF = "off"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)

    posts = relationship("Posts", back_populates="user")
    comments = relationship("Comments", back_populates="user")
    autoreply = relationship("AutoReply", back_populates="user")


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(Status), nullable=False)

    comments = relationship("Comments", back_populates="post", cascade="all, delete")
    user = relationship("Users", back_populates="posts")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    status = Column(Enum(Status), nullable=False)

    post = relationship("Posts", back_populates="comments")
    user = relationship("Users", back_populates="comments")


class AutoReply(Base):
    __tablename__ = "autoreply"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(AutoReplyStatus), nullable=False, default=AutoReplyStatus.OFF)
    timer = Column(Interval)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("Users", back_populates="autoreply")
