from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class ChatBase(SQLModel):
    owner_id: UUID = Field(foreign_key="user.id")
    title: str = Field(max_length=255)


class TitleUpdate(SQLModel):
    chat_id: UUID
    title: str


class MessageBase(SQLModel):
    chat_id: UUID = Field(foreign_key="chat.id")
    role: str = Field(max_length=50)
    content: str
    sequence: int = Field(default=0, index=True)


class MessageInfo(SQLModel):
    role: str
    content: str
    sequence: int
    created_at: datetime


class MessageCreate(SQLModel):
    chat_id: UUID
    role: str
    content: str


class ChatCreate(ChatBase):
    pass


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
