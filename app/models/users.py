# 用户表
from pydantic import Field
from sqlmodel import SQLModel


class UserTable(SQLModel,table=True):
    id:int = Field(default=None,primary_key=True)
    username:str
    password:str
