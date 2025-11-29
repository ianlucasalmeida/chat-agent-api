from fastapi import HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.orchestrator import run_chat_pipeline
import logging

logger = logging.getLogger("ChatController")

class ChatController:
    @staticmethod
    async def handle_chat(request: ChatRequest) -> ChatResponse:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Mensagem vazia.")

        try:
            response_text = await run_chat_pipeline(request.message)
            return ChatResponse(response=response_text)
        except Exception as e:
            logger.error(f"Erro interno: {e}")
            raise HTTPException(status_code=500, detail="Erro processando solicitação.")