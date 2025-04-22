from fastapi import APIRouter, HTTPException
from email_validator import EmailNotValidError, validate_email

from app.models.response import ResponseBase
from app.models.response.user import CaptchaItem
from app.utils.email import send_email_captcha
from app.utils.logger import logger
from app.utils.security import Captcha, CaptchaInfo

router = APIRouter(tags=["captcha"])


@router.get(
    "/captcha/image",
    response_model=ResponseBase[CaptchaItem],
    summary="获取图形验证码",
)
async def generate_image_captcha():
    """生成图形验证码接口"""

    try:
        # 创建图形验证码对象(type为img)
        captcha = Captcha(type="image")

        # 获取验证码信息(包括id、code、base64)
        captcha_info: CaptchaInfo = captcha.get_captcha()
        logger.info(f"生成验证码成功: {captcha_info.code=}")
        return ResponseBase[CaptchaItem](
            data=CaptchaItem(
                captcha_id=captcha_info.id,
                captcha_img_base64=captcha_info.base64 or "",
            ),
        )
    except Exception as e:
        logger.error(f"生成验证码失败:\n {e}")
        raise HTTPException(status_code=500, detail="验证码生成失败")


@router.get(
    "/captcha/email",
    response_model=ResponseBase[CaptchaItem],
    summary="获取邮箱验证码",
)
async def generate_email_captcha(email: str):
    """生成邮箱验证码接口"""

    try:
        # 校验邮箱格式
        validate_email(email)

        # 创建图形验证码对象(type为img)
        captcha = Captcha(type="emails")

        # 获取验证码信息(包括id、code)
        captcha_info: CaptchaInfo = captcha.get_captcha()

        # 记录日志
        logger.info(f"生成验证码成功: {captcha_info.code=}")

        # 发送邮箱验证码
        send_email_captcha(email_to=email, captcha=captcha_info)

        return ResponseBase[CaptchaItem](
            data=CaptchaItem(
                captcha_id=captcha_info.id,
            ),
        )
    except EmailNotValidError as e:
        logger.error(f"邮箱格式错误:\n {e}")
        raise HTTPException(status_code=553, detail="邮箱格式错误")
    except Exception as e:
        logger.error(f"生成验证码失败:\n {e}")
        raise HTTPException(status_code=500, detail="验证码生成失败")
