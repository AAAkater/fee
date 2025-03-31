from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.models.token import TokenPayload


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
