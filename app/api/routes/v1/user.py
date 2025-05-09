from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db.main import SessionDep
from app.models.db_models.user import UserCreate
from app.models.request.user import UserRegisterBody
from app.models.response import ResponseBase
from app.models.response.user import TokenItem
from app.services import user_service
from app.utils import security
from app.utils.logger import logger
from app.utils.security import Captcha
from app.utils.token import create_access_token

router = APIRouter(tags=["user"])


@router.post(
    "/login",
    response_model=ResponseBase[TokenItem],
    summary="用户登录",
)
async def login(
    session: SessionDep,
    user_form: OAuth2PasswordRequestForm = Depends(),
) -> ResponseBase[TokenItem]:
    user = user_service.get_user_by_username(
        session=session,
        username=user_form.username,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误"
        )

    token = create_access_token(str(user.id))

    return ResponseBase[TokenItem](
        code="0",
        msg="ok",
        data=TokenItem(access_token=token, token_type="Bearer"),
    )


@router.post(
    "/register",
    status_code=status.HTTP_200_OK,
    response_model=ResponseBase,
    summary="用户注册",
)
async def register(
    session: SessionDep, new_user: UserRegisterBody
) -> ResponseBase:
    # 验证邮箱验证码
    if not Captcha.verify_captcha(new_user.email, new_user.email_captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱验证码错误"
        )

    # 验证图片验证码
    if not Captcha.verify_captcha(
        new_user.img_captcha_id, new_user.img_captcha_code
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="图片验证码错误"
        )

    # 检查用户名是否已存在
    user = user_service.get_user_by_username(
        session=session, username=new_user.username
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    try:
        user_service.create_new_user(
            session=session,
            new_user_info=UserCreate(
                username=new_user.username,
                email=new_user.email,
                password_hash=security.get_password_hash(new_user.password),
            ),
        )
    except Exception as e:
        logger.error(f"注册用户失败：{e}")
        raise HTTPException(status_code=500, detail="注册失败")

    return ResponseBase()
