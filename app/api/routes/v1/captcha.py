from fastapi import APIRouter, HTTPException
from app.utils.security import Captcha, CaptchaInfo

router = APIRouter()


@router.get("/captcha", response_model=CaptchaInfo)
async def generate_image_captcha(code_len: int = 4):
    """生成图形验证码接口"""
    try:
        # 创建图形验证码对象(type为img)
        captcha = Captcha(code_len=code_len, type="img")

        # 获取验证码信息(包括id、code、base64)
        captcha_info = captcha.get_captcha()

        # 确保返回的 base64 存在以及包含 MIME 前缀(浏览器才能识别这是一个图片)
        if captcha_info.base64 and not captcha_info.base64.startswith(
            "data:image/png"
        ):
            captcha_info.base64 = f"data:image/png;base64,{captcha_info.base64}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证码生成失败: {str(e)}")

    return {
        "code": "0",
        "msg": "ok",
        "data": {
            "captcha_id": captcha_info.id,
            "captcha_img_base64": captcha_info.base64,
        },
    }
