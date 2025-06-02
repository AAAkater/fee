import uuid
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.db_models.chat import ChatBase, MessageBase
from app.models.db_models.user import UserBase


class CommonFields(SQLModel):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    is_deleted: bool = Field(default=False, nullable=False)
    deleted_at: datetime | None = Field(default=None, nullable=True)
    status: str = Field(default="active", max_length=50, nullable=False)


# 用户表
class User(UserBase, CommonFields, table=True):
    chats: List["Chat"] = Relationship(back_populates="user")


# 会话记录表
class Chat(ChatBase, CommonFields, table=True):
    user: User = Relationship(back_populates="chats")
    messages: List["Message"] = Relationship(back_populates="chat")


# 对话历史表
class Message(MessageBase, CommonFields, table=True):
    chat: Chat = Relationship(back_populates="messages")
