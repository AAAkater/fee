from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import BaseModel, ValidationError

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(f"{settings.API_VER_STR}/login")


TokenDep = Annotated[str, Depends(oauth2_scheme)]


class TokenPayload(BaseModel):
    exp: datetime
    user_id: str


def create_access_token(user_id: str) -> str:
    """_summary_

    Args:
        subject (str): _description_

    Returns:
        str: _description_
    """
    expired_time = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = TokenPayload(exp=expired_time, user_id=user_id).model_dump()
    encode_jwt: str = jwt.encode(
        claims=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encode_jwt


def get_access_token_info(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=settings.ALGORITHM,
        )
        return TokenPayload(**payload)
    except (ExpiredSignatureError, JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期或失效"
        )
