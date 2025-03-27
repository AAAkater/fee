
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Engine, select
from sqlmodel import Session

from example.app.models.users import UserTable

def create_user(register_form:OAuth2PasswordRequestForm = Depends()):
    # 创建数据库会话
    with Session(Engine) as session:
        # 检查用户是否存在
        user = session.exec(select(UserTable).where(UserTable.username == register_form.username)).first()
        if user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建新用户
    new_user = UserTable(
        username=register_form.username,
        password=register_form.password 
    )
    session.add(new_user)
    session.commit()
