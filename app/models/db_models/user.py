from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(max_length=255, unique=True)
    email: str = Field(max_length=255, unique=True)
    password_hash: str = Field(max_length=255)


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    username: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    password_hash: str | None = Field(default=None, max_length=255)
