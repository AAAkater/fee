from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.db.main import CurrentUser, SessionDep
from app.models.db_models.chat import ChatCreate, MessageCreate
from app.models.response import ResponseBase
from app.services import chat_service
from app.utils.logger import logger

router = APIRouter(tags=["chat"])


@router.post("/chat", summary="创建新的对话")
async def create_new_chat(
    session: SessionDep,
    current_user: CurrentUser,
):
    chat = ChatCreate(owner_id=current_user.id, title="New Chat")
    try:
        chat_service.create_new_chat(session=session, new_chat_info=chat)
    except Exception as e:
        logger.error(f"创建对话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话失败",
        )
    return ResponseBase()


@router.post(
    "/chat/messages",
    summary="添加消息",
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
        logger.error(f"添加消息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加消息失败",
        )
    return ResponseBase()


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
        logger.error(f"获取消息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取消息失败",
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
        logger.error(f"获取对话列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话列表失败",
        )
