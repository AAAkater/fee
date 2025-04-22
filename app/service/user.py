from app.db.postgres_client import SessionDep
from app.db.tables import User
from app.models.db_models.user import UserCreate


def create_new_user(*, sessions: SessionDep, new_user_info: UserCreate):
    new_user = User.model_validate(new_user_info)

    sessions.add(new_user)
    sessions.commit()
