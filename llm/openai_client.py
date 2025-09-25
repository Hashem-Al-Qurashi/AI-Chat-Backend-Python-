from typing import Optional
import openai
from openai import OpenAI
from llm.base import LLMClient, LLMConfig, LLMResponse
import structlog
import tiktoken

logger = structlog.get_logger()

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, default_model: str = "gpt-4o-mini"):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)
        self.default_model = default_model
        self.encoder = None
        
    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        model = config.model or self.default_model
        
        try:
            messages = []
            if config.system_prompt:
                messages.append({"role": "system", "content": config.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
            
            if config.top_p is not None:
                kwargs["top_p"] = config.top_p
                
            response, elapsed_ms = self._measure_time(
                self.client.chat.completions.create,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else self.count_tokens(content)
            
            logger.info(
                "openai_generation_complete",
                model=model,
                tokens=tokens_used,
                response_time_ms=elapsed_ms
            )
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                response_time_ms=elapsed_ms
            )
            
        except openai.RateLimitError as e:
            logger.error("openai_rate_limit", error=str(e))
            raise Exception(f"Rate limit exceeded: {e}")
        except openai.AuthenticationError as e:
            logger.error("openai_auth_error", error=str(e))
            raise Exception(f"Authentication failed: {e}")
        except Exception as e:
            logger.error("openai_generation_error", error=str(e))
            raise Exception(f"Generation failed: {e}")
            
    def count_tokens(self, text: str) -> int:
        try:
            if not self.encoder:
                self.encoder = tiktoken.encoding_for_model(self.default_model)
            return len(self.encoder.encode(text))
        except:
            return len(text) // 4