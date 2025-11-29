from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.controllers.chat_controller import ChatController

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    return await ChatController.handle_chat(payload)