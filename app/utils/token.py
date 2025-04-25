from datetime import datetime, timedelta, timezone

import jose
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.core.config import settings
from app.models.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(f"{settings.API_VER_STR}/login")


def create_access_token(subject: str) -> str:
    """_summary_

    Args:
        subject (str): _description_

    Returns:
        str: _description_
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = TokenPayload(
        exp=expire,
        sub=str(subject),
    ).model_dump()
    encode_jwt: str = jwt.encode(
        claims=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encode_jwt


def get_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=settings.ALGORITHM,
        )
    except jose.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token已过期"
        )
    return payload
