import secrets

from pydantic import PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "AI system"

    # POSTGRESQL
    POSTGRESQL_USER: str = "postgres"
    POSTGRESQL_PASSWORD: str = ""
    POSTGRESQL_PROT: int = 5432
    POSTGRESQL_SERVER: str = "127.0.0.1"
    POSTGRESQL_DB: str = ""

    @computed_field
    @property
    def POSTGRESQL_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRESQL_USER,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PROT,
            path=self.POSTGRESQL_DB,
        )

    # REDIS
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_EXPIRE: int = 600

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            path=f"/{self.REDIS_DB}",
        )

    # EMAIL
    EMAIL_ENABLED: bool = False
    EMAIL_FROM_NAME: str = "system"
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    # TOKEN
    SECRET_KEY: str = secrets.token_urlsafe(nbytes=32)
    ALGORITHM: str = "HS256"
    # 60 minutes * 24 hours * 8 days = 8 days 八天有效期
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_VER_STR: str = "/api/v1"

    # LLM
    MODEL_API_KEY: str = ""
    MODEL_BASE_URL: str = ""
    MODEL_NAME: str = ""


settings = Settings()


if __name__ == "__main__":
    url = settings.POSTGRESQL_URI

    print(url)
