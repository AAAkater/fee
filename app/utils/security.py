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
    """
    Hashes a password using the configured password hashing context.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies if the provided password matches the hashed password.

    Args:
        password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return pwd_context.verify(password, hashed_password)


class CaptchaInfo(BaseModel):
    id: str
    code: str
    base64: str | None = None


class Captcha:
    """
    A class for generating and verifying CAPTCHAs (Completely Automated Public Turing tests).

    This class provides functionality to generate CAPTCHA codes either as text or images,
    and includes methods for verification. The CAPTCHA can be customized in length and type.

    Attributes:
        id (str): A unique identifier for the CAPTCHA instance.
        code_len (int): The length of the CAPTCHA code (default: 4).
        type (Literal["image", "email"]): The type of CAPTCHA to generate (default: "image").
        code (str): The generated CAPTCHA code.

    Methods:
        generate_code: Generates a random CAPTCHA code.
        generate_img_base64: Generates a base64-encoded image of the CAPTCHA code.
        get_captcha: Retrieves CAPTCHA information based on the specified type.
        verify_captcha: Verifies if the provided CAPTCHA code matches the stored one.
    """

    def __init__(
        self,
        code_len: int = 4,
        type: Literal["image", "email"] = "image",
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
        if self.type == "image":
            img_base64 = self.generate_img_base64
            return CaptchaInfo(
                id=self.id,
                code=self.code,
                base64=img_base64,
            )
        return CaptchaInfo(id=self.id, code=self.code)

    @staticmethod
    def verify_captcha(captcha_id: str, captcha_code: str) -> bool:
        """验证验证码"""
        code = r.get(name=captcha_id)
        r.delete(captcha_id)
        return code == captcha_code
