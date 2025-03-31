from pydantic import BaseModel


class UserRegisterBody(BaseModel):
    password: str
    username: str
    email: str
    email_captcha: str
    captcha_id: str
    img_captcha: str
