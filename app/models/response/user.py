import token

from pydantic import BaseModel


class TokenItem(BaseModel):
    access_token: str
    token_type: str = "Bearer"
