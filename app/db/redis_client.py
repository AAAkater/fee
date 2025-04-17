from redis import StrictRedis

from app.core.config import settings
from app.utils.logger import logger

r = StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


if __name__ == "__main__":
    print(f"{settings.REDIS_URL=}")

    if r.ping():
        logger.success("Redis连接成功")
