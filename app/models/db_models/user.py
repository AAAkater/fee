from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    user_id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=255, unique=True)
    email: str = Field(max_length=255, unique=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class UserCreate(UserBase):
    pass
