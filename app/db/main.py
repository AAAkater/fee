from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session

from app.db.postgres_client import get_db_session, init_tables, pg_engine
from app.db.redis_client import r
from app.utils.logger import logger


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
