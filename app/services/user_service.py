from sqlmodel import select

from app.db.main import Session
from app.models.db_models.tables import User
from app.models.db_models.user import UserCreate
from app.utils.security import verify_password


def create_new_user(*, session: Session, new_user_info: UserCreate):
    new_user = User.model_validate(new_user_info)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)


def get_user_by_username(*, session: Session, username: str) -> User | None:
    statements = select(User).where(User.username == username)
    select_user = session.exec(statements).first()

    return select_user


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
