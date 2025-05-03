import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session

from app.db.postgres_client import get_db_session, init_tables, pg_engine
from app.db.redis_client import r
from app.models.db_models.tables import User
from app.services import user_service
from app.utils.logger import logger
from app.utils.token import TokenDep, get_access_token_info


@asynccontextmanager
async def init_db(_: FastAPI):
    """
    初始化数据库
    :return:
    """

    # 创建所有表
    try:
        init_tables()
        if not r.ping():
            raise Exception("Redis连接失败")
        logger.success("数据库初始化成功")

    except Exception as e:
        logger.error(f"数据库初始化失败\n {e}")
        exit(1)
    yield
    # 关闭数据库连接
    pg_engine.dispose()
    logger.success("PostgreSQL连接关闭")
    # 关闭Redis连接
    r.close()
    logger.success("Redis连接关闭")


SessionDep = Annotated[Session, Depends(get_db_session)]


def get_current_active_user(session: SessionDep, token: TokenDep):
    payload = get_access_token_info(token)

    user = user_service.get_user_by_id(
        session=session, user_id=uuid.UUID(payload.user_id)
    )

    if not user:
        logger.error("用户不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_active_user)]
