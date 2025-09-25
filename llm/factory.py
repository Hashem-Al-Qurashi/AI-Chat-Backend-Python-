from typing import Optional
from llm.base import LLMClient
from llm.openai_client import OpenAIClient
from llm.anthropic_client import AnthropicClient
from app.config import settings
import structlog

logger = structlog.get_logger()

def get_llm_client(provider: Optional[str] = None) -> LLMClient:
    provider = provider or settings.llm_provider
    
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        logger.info("creating_openai_client")
        return OpenAIClient(settings.openai_api_key)
    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        logger.info("creating_anthropic_client")
        return AnthropicClient(settings.anthropic_api_key)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")