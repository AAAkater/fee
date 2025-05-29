from uuid import UUID

from pydantic import BaseModel


class UserQueryBody(BaseModel):
    chat_id: UUID
    role: str
    content: str


class UpdateTitleRequest(BaseModel):
    chat_id: UUID
    update_title: str
