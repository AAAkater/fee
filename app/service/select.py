
from sqlalchemy import Engine, select
from sqlmodel import Session
from example.app.models.users import UserTable


def select_user_from_username(username:str,password:str):
    with Session(Engine) as session:
        
        # 从数据库中查询是否有该用户
        user = session.exec(select(UserTable).where(UserTable.username == username)).first()
        
        if user and user.password == password:
            return True
    
    return False
