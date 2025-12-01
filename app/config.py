from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Chat Agent API"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Nova sintaxe do Pydantic V2 (remove o warning)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()