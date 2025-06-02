from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatInfoItem(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    updated_at: datetime
    created_at: datetime


class TitleUpdateItem(BaseModel):
    id: UUID
    title: str
    updated_at: datetime


class MessageItem(BaseModel):
    role: str
    content: str
    created_at: datetime
