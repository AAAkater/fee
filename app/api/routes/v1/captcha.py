from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, HTTPException, status

from app.db.redis_client import r
from app.models.response import ResponseBase
from app.models.response.user import CaptchaItem
from app.utils.email import send_email_captcha
from app.utils.logger import logger
from app.utils.security import Captcha, CaptchaInfo

router = APIRouter(tags=["captcha"])


@router.get(
    "/captcha/image",
    response_model=ResponseBase[CaptchaItem],
    status_code=status.HTTP_200_OK,
    summary="获取图形验证码",
)
async def generate_image_captcha() -> ResponseBase[CaptchaItem]:
    """生成图形验证码接口"""

    try:
        # 创建图形验证码对象(type为img)
        captcha = Captcha(type="image")

        # 获取验证码信息(包括id、code、base64)
        captcha_info: CaptchaInfo = captcha.get_captcha()
        logger.success(f"生成验证码成功: {captcha_info.code=}")
        # 有效期120秒
        r.setex(name=captcha_info.id, time=120, value=captcha_info.code)

        return ResponseBase[CaptchaItem](
            data=CaptchaItem(
                captcha_id=captcha_info.id,
                captcha_img_base64=captcha_info.base64 or "",
            ),
        )
    except Exception as e:
        logger.error(f"生成验证码失败:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码生成失败",
        )


@router.get(
    "/captcha/email",
    response_model=ResponseBase,
    status_code=status.HTTP_200_OK,
    summary="获取邮箱验证码",
)
async def generate_email_captcha(email: str) -> ResponseBase:
    """生成邮箱验证码接口"""

    try:
        # 校验邮箱格式
        _ = validate_email(email)
    except EmailNotValidError as e:
        logger.error(f"邮箱格式错误:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱格式错误"
        )

    try:
        # 创建图形验证码对象(type为email)
        captcha = Captcha(type="email")

        # 获取验证码信息(包括id、code)
        captcha_info: CaptchaInfo = captcha.get_captcha()

        # 记录日志
        logger.success(f"生成验证码成功: {captcha_info.code=}")

        # 发送邮箱验证码
        send_email_captcha(email_to=email, captcha=captcha_info)
        # 有效期120秒
        r.setex(name=email, time=120, value=captcha_info.code)
        return ResponseBase()
    except Exception as e:
        logger.error(f"邮箱验证码发送失败:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮箱验证码发送失败",
        )
