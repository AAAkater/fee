from typing import Literal

from fastapi import APIRouter, HTTPException

from app.models.response import ResponseBase
from app.models.response.user import CaptchaItem
from app.utils.logger import logger
from app.utils.security import Captcha, CaptchaInfo

router = APIRouter(tags=["captcha"])


@router.get(
    "/captcha/{captcha_type}",
    response_model=ResponseBase[CaptchaItem],
    summary="获取图形验证码",
)
async def generate_image_captcha(captcha_type: Literal["img", "email"] = "img"):
    """生成图形验证码接口"""

    if captcha_type != "img":
        logger.error(f"验证码类型不支持: {captcha_type}")
        raise HTTPException(status_code=400, detail="验证码类型不支持")
    try:
        # 创建图形验证码对象(type为img)
        captcha = Captcha(type="img")

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
