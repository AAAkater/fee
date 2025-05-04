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
    Initialize and manage database connections for the application.

    This coroutine function initializes database tables, checks Redis connection,
    and ensures proper disposal of connections upon completion. It is designed to be used
    as a dependency in FastAPI applications.

    Args:
        _ (FastAPI): FastAPI application instance (unused).

    Yields:
        None: This is a generator function that yields control back to the caller.

    Raises:
        Exception: If Redis connection fails or any other database initialization error occurs.
        SystemExit: If database initialization fails, the application will exit with code 1.

    Notes:
        - The function will attempt to initialize database tables and verify Redis connection.
        - On success, it yields control and manages connection cleanup when the context exits.
        - On failure, it logs the error and terminates the application.
        - Both PostgreSQL and Redis connections are properly closed when the context exits.
    """
    try:
        # Create all tables
        init_tables()
        if not r.ping():
            raise Exception("Redis connection failed")
        logger.success("Database initialization successful")

    except Exception as e:
        logger.error(f"Database initialization failed:\n{e}")
        exit(1)
    yield
    pg_engine.dispose()
    logger.success("PostgreSQL connection closed")
    r.close()
    logger.success("Redis connection closed")


SessionDep = Annotated[Session, Depends(get_db_session)]


def get_current_active_user(session: SessionDep, token: TokenDep) -> User:
    """
    Retrieves the currently active user based on the provided session and token.

    Args:
        session (SessionDep): The database session dependency.
        token (TokenDep): The access token dependency containing user information.

    Returns:
        User: The user object corresponding to the authenticated user.

    Raises:
        HTTPException: If the user is not found in the database (status code 404).

    Notes:
        - The function decodes the user ID from the access token payload.
        - Uses the user service to fetch the user from the database.
        - Logs an error if the user lookup fails.
    """
    payload = get_access_token_info(token)

    try:
        user = user_service.get_user_by_id(
            session=session, user_id=uuid.UUID(payload.user_id)
        )
    except Exception as e:
        logger.error(f"User not found:\n:{e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_active_user)]
