import base64
import random
import string
import uuid
from io import BytesIO
from typing import Literal

from captcha.image import ImageCaptcha
from passlib.context import CryptContext
from PIL.Image import Image
from pydantic import BaseModel

from app.db.redis_client import r

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """生成密码的哈希值"""
    return pwd_context.hash(password)


class CaptchaInfo(BaseModel):
    id: str
    code: str
    base64: str | None = None


class Captcha:
    def __init__(
        self,
        code_len: int = 4,
        type: Literal["img", "email"] = "img",
    ):
        self.id = uuid.uuid4().hex
        self.code_len = code_len
        self.type = type
        self.code = self.generate_code

    @property
    def generate_code(self) -> str:
        """生成验证码"""
        chr_all = string.ascii_letters + string.digits
        return "".join(random.choices(population=chr_all, k=self.code_len))

    @property
    def generate_img_base64(self) -> str:
        """生成验证码图片base64"""
        image_captcha = ImageCaptcha()
        img: Image = image_captcha.generate_image(chars=self.code)

        out_buffer = BytesIO()
        img.save(out_buffer, format="PNG")
        byte_data: bytes = out_buffer.getvalue()
        base64_str: str = base64.b64encode(byte_data).decode(encoding="utf-8")
        return base64_str

    def get_captcha(self) -> CaptchaInfo:
        """获取验证码"""
        if self.type == "img":
            img_base64 = self.generate_img_base64
            r.setex(name=self.id, time=120, value=self.code)
            return CaptchaInfo(
                id=self.id,
                code=self.code,
                base64=img_base64,
            )

        # elif self.type == "email":
        #     r.setex(name=self.id, time=120, value=self.code)

        return CaptchaInfo(id=self.id, code=self.code)

    @staticmethod
    def verify_captcha(captcha_id: str, captcha_code: str) -> bool:
        """验证验证码"""
        code = r.get(name=captcha_id)
        r.delete(captcha_id)
        return code == captcha_code
