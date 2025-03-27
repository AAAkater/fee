from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from crud import select_user_from_username
from dotenv import load_dotenv
import os
from core.config import settings


load_dotenv('.env')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(tags=["login"])  

# 用户登录接口
@router.post("/token")
async def login(login_form:OAuth2PasswordRequestForm = Depends()):# 传入一个请求表单

    result=select_user_from_username(login_form.username,login_form.password)# 进行数据库校验

    if result==False:
        raise HTTPException(status_code=401,detail="用户名或密码不正确！",headers={"WWW-Authenticate": "Bearer"})
    
    # 令牌过期时间
    token_expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    #加密的数据包括用户名及令牌过期时间
    token_data = {
        "username":login_form.username,
        "exp":token_expires
    }

    token=jwt.encode(token_data,os.getenv(settings.SECRET_KEY),os.getenv("ALGORITHMS"))#生成加密字符串

    return {"加密字符串为":token}

# 获取加密令牌中的用户名
def get_current_username(token:str = Depends(oauth2_scheme)):
        
        
        try:
            token_data = jwt.decode(token,os.getenv(settings.SECRET_KEY),[os.getenv("ALGORITHMS")])# 解密
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="无效的Token")

    
        username = token_data.get("username",None)

        #无用户情况
        if not username:
            raise HTTPException(status_code=401,detail="未找到用户",headers={"WWW-Authenticate": "Bearer"})
        return username
        
