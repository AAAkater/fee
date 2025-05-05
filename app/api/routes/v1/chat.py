from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.db.main import CurrentUser, SessionDep
from app.models.db_models.chat import ChatCreate, MessageCreate
from app.models.response import ResponseBase
from app.models.response.chat import ChatItem, ChatMessage
from app.services import chat_service
from app.utils.logger import logger

router = APIRouter(tags=["chat"])


@router.post("/chat", summary="Create a new chat")
async def create_new_chat(
    session: SessionDep,
    current_user: CurrentUser,
) -> ResponseBase[ChatItem]:
    """
    Creates a new chat for the current user.

    Args:
        session (SessionDep): Database session dependency.
        current_user (CurrentUser): Authenticated current user.

    Returns:
        ResponseBase[ChatItem]: Response containing the newly created chat item.

    Raises:
        HTTPException: If an error occurs during chat creation, raises a 500 Internal Server Error.

    Note:
        The new chat will be initialized with a default title of "New Chat".
    """
    try:
        chat = chat_service.create_new_chat(
            session=session,
            new_chat_info=ChatCreate(
                owner_id=current_user.id, title="New Chat"
            ),
        )
    except Exception as e:
        logger.error(f"Failed to create a new chat:\n{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create a new chat",
        )
    return ResponseBase[ChatItem](
        data=ChatItem(id=chat.id, title=chat.title, created_at=chat.created_at)
    )


@router.post(
    "/chat/messages",
    summary="Add messages",
)
async def add_message(
    session: SessionDep,
    current_user: CurrentUser,
    new_message_body: MessageCreate,
):
    try:
        chat_service.add_message_to_chat(
            session=session, new_message=new_message_body
        )
    except Exception as e:
        logger.error(f"Failed to add messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add messages",
        )
    return ResponseBase[ChatMessage](
        data=ChatMessage(
            chat_id=current_user.id, role=current_user, content=new_message_body
        )
    )


@router.get("/chat/messages")
async def get_chat_messages(
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: UUID,
):
    try:
        messages = chat_service.get_messages_from_chat(
            session=session, chat_id=chat_id
        )
        return ResponseBase(data=messages)
    except Exception as e:
        logger.error(f"Failed to get the messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the messages",
        )


@router.get("/chats")
async def get_user_chats(
    session: SessionDep,
    current_user: CurrentUser,
):
    try:
        chats = chat_service.get_chats_by_user_id(
            session=session, user_id=current_user.id
        )
        return ResponseBase(data=chats)
    except Exception as e:
        logger.error(f"Failed to get conversation list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation list",
        )
