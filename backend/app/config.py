from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    LLM_API_KEY: str
    TAVILY_API_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()