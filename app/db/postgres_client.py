from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

pg_engine: Engine = create_engine(url=str(settings.POSTGRESQL_URI))


def get_db_session():
    """
    Generator function to yield a database session.

    This function creates a context-managed database session using the provided PostgreSQL engine.
    The session is yielded for use in database operations, ensuring proper cleanup after use.

    Yields:
        sqlalchemy.orm.Session: A SQLAlchemy database session object.

    Example:
        >>> for session in get_db_session():
        ...     # perform database operations
        ...     pass
    """
    with Session(pg_engine) as session:
        yield session


def init_tables():
    """
    Initializes database tables by creating all tables defined in SQLModel metadata.

    This function uses SQLModel's metadata to create all the database tables that have been
    defined in the application's SQLModel classes. The tables are created in the database
    connected through the global pg_engine instance.

    Note:
        This function should typically be called once during application startup to ensure
        all required database tables exist before the application starts processing requests.

    Raises:
        SQLAlchemyError: If there is any error during the table creation process.
    """
    SQLModel.metadata.create_all(pg_engine)
