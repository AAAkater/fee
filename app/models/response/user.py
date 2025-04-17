from pydantic import BaseModel


class TokenItem(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class CaptchaItem(BaseModel):
    captcha_id: str
    captcha_img_base64: str
