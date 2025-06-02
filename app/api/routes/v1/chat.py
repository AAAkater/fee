from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sse_starlette import EventSourceResponse

from app.db.main import CurrentUser, SessionDep
from app.models.db_models.chat import ChatCreate, MessageCreate, MessageInfo
from app.models.request.chat import TitleUpdateBody, UserQueryBody
from app.models.response import ResponseBase
from app.models.response.chat import ChatInfoItem, TitleUpdateItem
from app.services import chat_service
from app.utils.logger import logger
from app.utils.model import generate_chat_title, generate_model_response_stream

router = APIRouter(tags=["chat"])


@router.post("/chat", summary="Create a new chat")
async def create_new_chat(
    session: SessionDep,
    current_user: CurrentUser,
) -> ResponseBase[ChatInfoItem]:
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
        chat_info = chat_service.create_new_chat(
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
    return ResponseBase[ChatInfoItem](data=chat_info)


@router.post(
    "/chat/messages",
    summary="Add messages",
)
async def add_message(
    session: SessionDep,
    current_user: CurrentUser,
    user_query_body: UserQueryBody,
    background_tasks: BackgroundTasks,
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

    # If this is the first conversation, generate a title
    if (
        chat_service.count_chat_messages(
            session=session, chat_id=user_query_body.chat_id
        )
        == 0
    ):
        try:
            title = await generate_chat_title(user_query_body.content)
            chat_service.update_chat_title_by_chat_id(
                session=session,
                chat_id=user_query_body.chat_id,
                new_title=title,
            )
            logger.success(f"Chat title generated successfully:{title}")
        except Exception as e:
            logger.error(f"Failed to generate chat title:{e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate chat title",
            )

    # add the user message to the chat
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
        # retrieve all messages from the chat
        messages: list[MessageInfo] = chat_service.get_messages_from_chat(
            session=session, chat_id=user_query_body.chat_id
        )
    except Exception as e:
        logger.error(f"Failed to add messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add messages",
        )

    async def stream_and_save():
        full_content = ""

        async for chunk in generate_model_response_stream(messages):
            full_content += chunk
            yield chunk

        background_tasks.add_task(
            chat_service.add_message_to_chat,
            session=session,
            new_message=MessageCreate(
                chat_id=user_query_body.chat_id,
                role="assistant",
                content=full_content,
                sequence=0,
            ),
        )

    return EventSourceResponse(
        stream_and_save(),
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
    except Exception as e:
        logger.error(f"Failed to get the messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get the messages",
        )
    return ResponseBase[list[MessageInfo]](data=messages)


@router.get("/chats")
async def get_user_chats(
    session: SessionDep,
    current_user: CurrentUser,
):
    try:
        chat_infos = chat_service.get_chats_by_user_id(
            session=session, user_id=current_user.id
        )
        return ResponseBase[list[ChatInfoItem]](data=chat_infos)
    except Exception as e:
        logger.error(f"Failed to get conversation list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation list",
        )


@router.post("/chat/title")
async def update_chat_title(
    session: SessionDep,
    current_user: CurrentUser,
    title_update_body: TitleUpdateBody,
):
    try:
        db_chat = chat_service.get_chat_by_chat_id(
            session=session, chat_id=title_update_body.chat_id
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
        new_db_chat = chat_service.update_chat_title_by_chat_id(
            session=session,
            chat_id=title_update_body.chat_id,
            new_title=title_update_body.new_title,
        )
    except Exception as e:
        logger.error(f"Failed to update the title: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update the title",
        )
    return ResponseBase[TitleUpdateItem](
        data=TitleUpdateItem(
            id=new_db_chat.id,
            title=new_db_chat.title,
            updated_at=new_db_chat.updated_at,
        )
    )
