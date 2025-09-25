from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"
    log_level: str = "INFO"
    redis_url: Optional[str] = None
    max_concurrent_users: int = 10
    
    default_temperature: float = 0.7
    default_max_tokens: int = 500
    
    memory_retrieval_timeout_ms: int = 200
    total_response_timeout_ms: int = 3000

    class Config:
        env_file = ".env"

settings = Settings()