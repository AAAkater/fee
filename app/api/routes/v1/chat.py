from fastapi import APIRouter

router = APIRouter(tags=["chat"])


@router.post("/chat")
def create_new_chat():
    pass
