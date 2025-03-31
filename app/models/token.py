from datetime import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    exp: datetime
    sub: str
