
from sqlalchemy import Engine, select
from sqlmodel import Session
from db.tables import User


def select_user_from_username(username:str,password_hash:str):
    with Session(Engine) as session:
        
        # 从数据库中查询是否有该用户
        user = session.exec(select(User).where(User.username == username)).first()
        
        if user and user.password_hash == password_hash:
            return True
    
    return False
