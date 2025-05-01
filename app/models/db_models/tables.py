from datetime import datetime, timezone
from typing import List

from sqlmodel import Field, Relationship, SQLModel

from app.models.db_models.user import UserBase


# 用户表
class User(UserBase, table=True):
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    # 定义与 Session 的一对多关系
    sessions: List["Session"] = Relationship(back_populates="user")


# 会话记录表
class Session(SQLModel, table=True):
    session_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    title: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    # 定义与 User 的多对一关系
    user: User = Relationship(back_populates="sessions")

    # 定义与 Message 的一对多关系
    messages: List["Message"] = Relationship(back_populates="session")


# 对话历史表
class Message(SQLModel, table=True):
    message_id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="session.session_id")
    role: str = Field(max_length=50)  # 'user' 或 'assistant'
    content: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # 定义与 Session 的多对一关系
    session: Session = Relationship(back_populates="messages")
