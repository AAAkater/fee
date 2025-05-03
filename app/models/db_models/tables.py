import uuid
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.db_models.chat import ChatBase, MessageBase
from app.models.db_models.user import UserBase


class UpdateField(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


# 用户表
class User(UserBase, UpdateField, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chats: List["Chat"] = Relationship(back_populates="user")


# 会话记录表
class Chat(ChatBase, UpdateField, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: User = Relationship(back_populates="chats")
    messages: List["Message"] = Relationship(back_populates="chat")


# 对话历史表
class Message(MessageBase, UpdateField, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    chat: Chat = Relationship(back_populates="messages")
