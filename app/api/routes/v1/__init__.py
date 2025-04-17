from fastapi import APIRouter

from app.api.routes.v1 import captcha, chat, user

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(user.router)
v1_router.include_router(chat.router)
v1_router.include_router(captcha.router)
