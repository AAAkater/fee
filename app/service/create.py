
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Engine, select
from sqlmodel import Session

from db.tables import User

def create_user(register_form:OAuth2PasswordRequestForm = Depends()):
    # 创建数据库会话
    with Session(Engine) as session:
        # 检查用户是否存在
        user = session.exec(select(User).where(User.username == register_form.username)).first()
        if user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建新用户
    new_user = User(
        username=register_form.username,
        password_hash=register_form.password_hash
    )
    session.add(new_user)
    session.commit()
