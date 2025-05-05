from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatItem(BaseModel):
    id: UUID
    title: str
    created_at: datetime


class ChatMessage(BaseModel):
    chat_id: str
    role: str
    content: str
