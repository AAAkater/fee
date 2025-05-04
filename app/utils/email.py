import emails

from app.core.config import settings
from app.utils.logger import logger
from app.utils.security import CaptchaInfo


def get_email_template(code: str) -> str:
    return f"""
        <html>
        <body>
            <p>验证码:{code}</p>
            <p>60秒后失效</p>
        </body>
        </html>
    """


def send_email_captcha(
    *,
    email_to: str,
    captcha: CaptchaInfo,
) -> None:
    """
    Sends an email containing a CAPTCHA code to the specified recipient.

    Args:
        email_to (str): The email address of the recipient.
        captcha (CaptchaInfo): An object containing the CAPTCHA code to be sent.

    Raises:
        AssertionError: If email functionality is not enabled in the settings.
        Exception: If the email fails to send (non-250 status code).

    Notes:
        - Requires email configuration in settings (SMTP credentials, etc.).
        - Uses a predefined email template for the CAPTCHA message.
        - The email subject is hardcoded as "用户注册" (User Registration).
        - Logs errors if email sending fails.
    """
    assert settings.EMAIL_ENABLED, (
        "no provided configuration for email variables"
    )
    email_subject = "用户注册"
    html_template = get_email_template(captcha.code)
    message = emails.Message(
        subject=email_subject,
        html=html_template,
        mail_from=(settings.EMAIL_FROM_NAME, settings.SMTP_USERNAME),
    )
    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "tls": settings.SMTP_TLS,
        "ssl": settings.SMTP_SSL,
        "user": settings.SMTP_USERNAME,
        "password": settings.SMTP_PASSWORD,
    }
    response = message.send(to=email_to, smtp=smtp_options)
    if response.status_code != 250:
        logger.error(f"send email error: {response}")
        raise Exception(f"send email error: {response}")


if __name__ == "__main__":
    test_email = ""

    test_captcha = CaptchaInfo(code="abcd", id="123456")
    try:
        send_email_captcha(
            email_to=test_email,
            captcha=test_captcha,
        )
    except Exception as e:
        logger.error(e)
        exit(0)
    logger.success("Email sent successfully")
