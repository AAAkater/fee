from fastapi import APIRouter

from app.api.routes.v2 import test

v2_router = APIRouter(
    prefix="/v2",
)

v2_router.include_router(test.router)
