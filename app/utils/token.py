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
    """
    Generates a JWT access token for the given user ID.

    The token contains an expiration time based on the configured ACCESS_TOKEN_EXPIRE_MINUTES
    setting and is signed using the application's SECRET_KEY and ALGORITHM settings.

    Args:
        user_id: The unique identifier of the user for whom the token is being generated.

    Returns:
        str: A JWT encoded string containing the user ID and expiration time.

    Note:
        The token payload follows the TokenPayload model structure, which includes
        the expiration timestamp (exp) and user_id fields.
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
    """Decodes and validates a JWT access token.

    Args:
        token (str): The JWT access token to decode and validate.

    Returns:
        TokenPayload: A TokenPayload object containing the decoded token payload.

    Raises:
        HTTPException: If the token is expired, invalid, or fails validation.
            The exception will have status code 401 (UNAUTHORIZED) and detail
            message "Token已过期或失效" (Token expired or invalid).
    """
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
