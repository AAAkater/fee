from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.core.config import settings

db_engine = create_engine(url=str(settings.SQLALCHEMY_DATABASE_URI))


def get_db_session():
    with Session(db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db_session)]
