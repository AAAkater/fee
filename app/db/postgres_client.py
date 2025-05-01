from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

pg_engine: Engine = create_engine(url=str(settings.POSTGRESQL_URI))


def get_db_session():
    with Session(pg_engine) as session:
        yield session


def init_tables():
    SQLModel.metadata.create_all(pg_engine)
