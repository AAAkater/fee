from uuid import UUID

from sqlmodel import select

from app.db.main import Session
from app.models.db_models.tables import User
from app.models.db_models.user import UserCreate, UserUpdate
from app.utils import security
from app.utils.security import verify_password


def create_new_user(*, session: Session, new_user_info: UserCreate):
    new_user = User.model_validate(new_user_info)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def get_user_by_username(*, session: Session, username: str) -> User:
    statements = select(User).where(User.username == username)
    select_user = session.exec(statements).one()

    return select_user


def get_user_by_id(*, session: Session, user_id: UUID) -> User:
    statements = select(User).where(User.id == user_id)
    select_user = session.exec(statements).one()

    return select_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statements = select(User).where(User.email == email)
    select_user = session.exec(statements).first()

    return select_user


def reset_user_password(
    *,
    session: Session,
    user_id: UUID,
    new_password: str,
) -> User | None:
    user = get_user_by_id(session=session, user_id=user_id)
    if not user:
        return None

    user.password_hash = security.get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def update_user_info(
    *,
    session: Session,
    user_id: UUID,
    new_user_info: UserUpdate,
) -> User | None:
    user = get_user_by_id(session=session, user_id=user_id)
    if not user:
        return None

    user_data = new_user_info.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = security.get_password_hash(password)
        extra_data["password_hash"] = hashed_password
    user.sqlmodel_update(user_data, update=extra_data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(
    *,
    session: Session,
    username: str,
    password: str,
) -> User | None:
    user = get_user_by_username(session=session, username=username)
    if not user:
        return None

    if not verify_password(
        password=password, hashed_password=user.password_hash
    ):
        return None

    return user
