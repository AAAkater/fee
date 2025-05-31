from uuid import UUID

from sqlmodel import Session, asc, desc, select

from app.models.db_models.chat import (
    ChatCreate,
    MessageCreate,
    MessageInfo,
    TitleUpdate,
)
from app.models.db_models.tables import Chat, Message


def create_new_chat(
    *,
    session: Session,
    new_chat_info: ChatCreate,
):
    new_chat = Chat.model_validate(new_chat_info)

    session.add(new_chat)
    session.commit()
    session.refresh(new_chat)
    return new_chat


def update_chat_title(*, session: Session, new_title_info: TitleUpdate):
    stmt = select(Chat).where(Chat.id == new_title_info.chat_id)
    db_chat = session.exec(stmt).one()
    new_chat_data = new_title_info.model_dump(exclude_unset=True)

    db_chat.sqlmodel_update(new_chat_data)
    session.add(db_chat)
    session.commit()


def delete_chat(
    *,
    session: Session,
    chat_id: UUID,
):
    stmt = select(Chat).where(Chat.id == chat_id)
    chat = session.exec(stmt).one()

    session.delete(chat)
    session.commit()


def get_messages_from_chat(
    *,
    session: Session,
    chat_id: UUID,
):
    stmt = (
        select(
            Message.sequence,
            Message.role,
            Message.content,
            Message.created_at,
        )
        .filter_by(chat_id=chat_id)
        .order_by(
            asc(Message.sequence),
            asc(Message.created_at),
        )
    )
    db_messages = session.exec(stmt).all()

    messages = [MessageInfo.model_validate(message) for message in db_messages]
    return messages


def get_last_message_from_chat(
    *,
    session: Session,
    chat_id: UUID,
):
    statement = (
        select(Message)
        .filter_by(chat_id=chat_id)
        .order_by(desc(Message.sequence), desc(Message.created_at))
        .limit(1)
    )
    latest_message = session.exec(statement).first()

    return latest_message


def add_message_to_chat(*, session: Session, new_message: MessageCreate):
    latest_message = get_last_message_from_chat(
        session=session, chat_id=new_message.chat_id
    )
    if latest_message:
        new_message.sequence = latest_message.sequence + 1

    db_message = Message.model_validate(new_message)

    session.add(db_message)
    session.commit()


def get_chats_by_user_id(
    *,
    session: Session,
    user_id: UUID,
):
    stmt = (
        select(Chat)
        .where(Chat.owner_id == user_id)
        .order_by(desc(Chat.created_at))
    )
    db_chats = session.exec(stmt).all()

    return db_chats


def get_chat_by_chat_id(
    *,
    session: Session,
    chat_id: UUID,
):
    stmt = select(Chat).where(Chat.id == chat_id)
    db_chat = session.exec(stmt).one()

    return db_chat


def update_chat_title_by_chat_id(
    *, session: Session, chat_id: UUID, new_title: str
):
    stmt = select(Chat).where(Chat.id == chat_id)
    db_chat = session.exec(stmt).one()
    db_chat.title = new_title
    session.add(db_chat)
    session.commit()
    session.refresh(db_chat)
    return db_chat
