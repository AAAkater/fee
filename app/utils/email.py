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
    logger.info(f"send email result: {response}")


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
