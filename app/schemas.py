from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    # 1. Limite de caracteres (Max 500 chars é suficiente para chat simples)
    # Isso evita payloads gigantes de ataque de buffer.
    message: str = Field(..., min_length=1, max_length=500, description="A mensagem do usuário")

    @field_validator('message')
    def prevent_empty_or_whitespace(cls, v):
        if not v.strip():
            raise ValueError('A mensagem não pode ser vazia ou apenas espaços.')
        return v

class ChatResponse(BaseModel):
    response: str