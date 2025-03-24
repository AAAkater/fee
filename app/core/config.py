import secrets

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # POSTGRESQL
    POSTGRESQL_USER: str = "postgres"
    POSTGRESQL_PASSWORD: str = ""
    POSTGRESQL_PROT: int = 5432
    POSTGRESQL_SERVER: str = "127.0.0.1"
    POSTGRESQL_DB: str = ""

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRESQL_USER,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PROT,
            path=self.POSTGRESQL_DB,
        )

    # EMAIL
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM_NAME: str | None = None

    # TOKEN
    SECRET_KEY: str = secrets.token_urlsafe(nbytes=32)
    # 60 minutes * 24 hours * 8 days = 8 days 八天有效期
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_VER_STR: str = "/api/v1"


settings = Settings()


if __name__ == "__main__":
    url = settings.SQLALCHEMY_DATABASE_URI

    print(url)
