from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

pg_engine = create_engine(url=str(settings.POSTGRESQL_URI))


def init_db(session: Session):
    SQLModel.metadata.create_all(pg_engine)


def get_db_session():
    with Session(pg_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db_session)]
