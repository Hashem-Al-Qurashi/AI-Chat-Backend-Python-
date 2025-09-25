from typing import Optional
import anthropic
from llm.base import LLMClient, LLMConfig, LLMResponse
import structlog

logger = structlog.get_logger()

class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, default_model: str = "claude-3-haiku-20240307"):
        super().__init__(api_key)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model
        
    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        model = config.model or self.default_model
        
        try:
            kwargs = {
                "model": model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if config.system_prompt:
                kwargs["system"] = config.system_prompt
                
            if config.top_p is not None:
                kwargs["top_p"] = config.top_p
                
            response, elapsed_ms = self._measure_time(
                self.client.messages.create,
                **kwargs
            )
            
            content = response.content[0].text if response.content else ""
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else self.count_tokens(content)
            
            logger.info(
                "anthropic_generation_complete",
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
            
        except anthropic.RateLimitError as e:
            logger.error("anthropic_rate_limit", error=str(e))
            raise Exception(f"Rate limit exceeded: {e}")
        except anthropic.AuthenticationError as e:
            logger.error("anthropic_auth_error", error=str(e))
            raise Exception(f"Authentication failed: {e}")
        except Exception as e:
            logger.error("anthropic_generation_error", error=str(e))
            raise Exception(f"Generation failed: {e}")
            
    def count_tokens(self, text: str) -> int:
        return len(text) // 4