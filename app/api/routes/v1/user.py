from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.db.postgres_client import SessionDep
from app.models.db_models.user import UserCreate
from app.models.request.user import UserRegisterBody
from app.models.response import ResponseBase
from app.models.response.user import TokenItem
from app.service.user import create_new_user
from app.utils import security
from app.utils.logger import logger
from app.utils.token import create_access_token

router = APIRouter(tags=["user"])


@router.post("/login", response_model=ResponseBase[TokenItem])
async def login(
    session: SessionDep,
    user_form: OAuth2PasswordRequestForm = Depends(),
) -> ResponseBase[TokenItem]:
    logger.info(f"用户登录：{user_form.username}")
    user_id = "12412412"

    token = create_access_token(subject=user_id)

    return ResponseBase[TokenItem](
        code="0",
        msg="ok",
        data=TokenItem(access_token=token, token_type="Bearer"),
    )


@router.post("/register", response_model=ResponseBase)
async def register(session: SessionDep, new_user: UserRegisterBody):
    logger.info(f"注册新用户：{new_user.username} {new_user.password}")

    try:
        create_new_user(
            sessions=session,
            new_user_info=UserCreate(
                username=new_user.username,
                email=new_user.email,
                password_hash=security.get_password_hash(new_user.password),
                created_at=datetime.now(timezone.utc),
            ),
        )
    except Exception as e:
        logger.error(f"注册用户失败：{e}")
        raise HTTPException(status_code=500, detail="注册失败")

    return ResponseBase
