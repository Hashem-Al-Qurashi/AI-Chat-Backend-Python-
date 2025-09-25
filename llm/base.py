from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import time

class LLMConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int = 500
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    top_p: Optional[float] = None

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    response_time_ms: float
    
class LLMClient(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    @abstractmethod
    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        raise NotImplementedError
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        raise NotImplementedError
        
    def _measure_time(self, func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        return result, elapsed_ms