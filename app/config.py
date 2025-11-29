from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Chat Agent API"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    class Config:
        env_file = ".env"

settings = Settings()