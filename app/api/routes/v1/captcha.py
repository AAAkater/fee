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
    summary="Get image verification code",
)
async def generate_image_captcha() -> ResponseBase[CaptchaItem]:
    """
    Generates an image-based CAPTCHA and returns its details.

    This asynchronous function creates an image CAPTCHA, stores the verification code in Redis
    with a 120-second expiration time, and returns the CAPTCHA details including its ID and
    base64-encoded image.

    Returns:
        ResponseBase[CaptchaItem]: A response object containing:
            - captcha_id: The unique identifier for the CAPTCHA
            - captcha_img_base64: The base64-encoded CAPTCHA image

    Raises:
        HTTPException: If CAPTCHA generation fails, raises a 500 Internal Server Error
            with detail message "verification code generation failed"

    Note:
        The CAPTCHA code is stored in Redis with the CAPTCHA ID as key and has a TTL of 120 seconds.
        The function logs both successful and failed generation attempts.
    """

    try:
        captcha = Captcha(type="image")

        captcha_info: CaptchaInfo = captcha.get_captcha()
        logger.success(
            f"Verification code generated successfully: {captcha_info.code=}"
        )
        # valid for 120 seconds
        r.setex(name=captcha_info.id, time=120, value=captcha_info.code)

        return ResponseBase[CaptchaItem](
            data=CaptchaItem(
                captcha_id=captcha_info.id,
                captcha_img_base64=captcha_info.base64 or "",
            ),
        )
    except Exception as e:
        logger.error(f"Verification code generation failed:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification code generation failed",
        )


@router.get(
    "/captcha/email",
    response_model=ResponseBase,
    status_code=status.HTTP_200_OK,
    summary="Get email verification code",
)
async def generate_email_captcha(email: str) -> ResponseBase:
    """
    Generates and sends an email captcha to the specified email address.

    Validates the email format, generates a captcha, sends it via email, and stores it in Redis with a 120-second expiration.

    Args:
        email (str): The recipient email address to send the captcha to.

    Returns:
        ResponseBase: An empty response indicating successful operation.

    Raises:
        HTTPException:
            - 400 Bad Request if the email format is invalid.
            - 500 Internal Server Error if captcha generation or email sending fails.

    Notes:
        - The captcha code is stored in Redis with the email as the key.
        - The captcha code expires after 120 seconds.
        - Logs success or error messages for debugging purposes.
    """

    try:
        # Verify email format
        _ = validate_email(email)
    except EmailNotValidError as e:
        logger.error(f"Email format error:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email format error"
        )

    try:
        captcha = Captcha(type="email")

        captcha_info: CaptchaInfo = captcha.get_captcha()

        logger.success(
            f"Verification code generated successfully: {captcha_info.code=}"
        )

        send_email_captcha(email_to=email, captcha=captcha_info)
        # valid for 120 seconds
        r.setex(name=email, time=120, value=captcha_info.code)
        return ResponseBase()
    except Exception as e:
        logger.error(f"Email verification code sending failed:\n {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification code sending failed",
        )
