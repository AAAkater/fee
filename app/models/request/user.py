from pydantic import BaseModel


class UserRegisterBody(BaseModel):
    username: str
    password: str
    email: str
    email_captcha_code: str
    img_captcha_id: str
    img_captcha_code: str
