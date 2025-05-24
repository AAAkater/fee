from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sse_starlette import EventSourceResponse

from app.db.main import CurrentUser, SessionDep
from app.models.db_models.chat import ChatCreate, MessageCreate
from app.models.request.chat import UserQueryBody
from app.models.response import ResponseBase
from app.models.response.chat import ChatItem
from app.services import chat_service
from app.utils.logger import logger
from app.utils.model import generate_model_response_stream

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
    user_query_body: UserQueryBody,
):
    try:
        db_chat = chat_service.get_chat_by_chat_id(
            session=session, chat_id=user_query_body.chat_id
        )
    except Exception as e:
        logger.error(f"Failed to get chat by chat_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if db_chat.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission"
        )
    try:
        chat_service.add_message_to_chat(
            session=session,
            new_message=MessageCreate(
                chat_id=user_query_body.chat_id,
                role=user_query_body.role,
                content=user_query_body.content,
                sequence=0,
            ),
        )
    except Exception as e:
        logger.error(f"Failed to add messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add messages",
        )

    return EventSourceResponse(
        generate_model_response_stream(user_query_body.content),
        ping=15,
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/chat/messages")
async def get_chat_messages(
    session: SessionDep,
    current_user: CurrentUser,
    chat_id: UUID,
):
    try:
        db_chat = chat_service.get_chat_by_chat_id(
            session=session, chat_id=chat_id
        )
    except Exception as e:
        logger.error(f"Failed to get chat by chat_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if db_chat.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No permission"
        )

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
