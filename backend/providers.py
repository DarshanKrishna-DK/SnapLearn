"""
AI Provider Abstraction Layer
Based on DeepTutor patterns for robust LLM integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ProviderType(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    FALLBACK = "fallback"

@dataclass
class LLMResponse:
    content: str
    model_used: str
    provider: str
    tokens_used: Optional[int] = None
    response_time: float = 0.0
    structured_output: Optional[Dict[str, Any]] = None
    thinking: Optional[str] = None

@dataclass
class LLMRequest:
    messages: List[Dict[str, str]]
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    response_format: Optional[str] = None  # "json" for structured output
    tools: Optional[List[Dict[str, Any]]] = None
    
class ProviderError(Exception):
    def __init__(self, message: str, provider: str, retryable: bool = False):
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable

class RateLimitError(ProviderError):
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        super().__init__(f"Rate limit exceeded for {provider}", provider, retryable=True)
        self.retry_after = retry_after

class BaseProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.rate_limit_tracker = {}
    
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    def check_rate_limit(self) -> bool:
        """Check if we're rate limited"""
        if self.name in self.rate_limit_tracker:
            reset_time = self.rate_limit_tracker[self.name]
            if time.time() < reset_time:
                return False
        return True
    
    def set_rate_limit(self, retry_after: int):
        """Set rate limit reset time"""
        self.rate_limit_tracker[self.name] = time.time() + retry_after

class GeminiProvider(BaseProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import google.generativeai as genai
            self.genai = genai
            api_key = config.get("api_key") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Gemini API key not found")
            genai.configure(api_key=api_key)
            self.model_name = config.get("model", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(self.model_name)
            self._available = True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        return self._available and self.check_rate_limit()
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        if not self.is_available():
            raise ProviderError("Gemini provider not available", "gemini")
        
        start_time = time.time()
        
        try:
            # Format messages for Gemini
            prompt_parts = []
            if request.system_prompt:
                prompt_parts.append(f"System: {request.system_prompt}")
            
            for msg in request.messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt_parts.append(f"Human: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
            
            prompt = "\n\n".join(prompt_parts)
            
            # Generate response
            generation_config = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens or 2048,
            }
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            response_time = time.time() - start_time
            
            # Try to parse structured output if requested
            structured_output = None
            if request.response_format == "json":
                try:
                    structured_output = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response from Gemini")
            
            return LLMResponse(
                content=content,
                model_used=self.model_name,
                provider="gemini",
                response_time=response_time,
                structured_output=structured_output
            )
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                self.set_rate_limit(60)  # Wait 1 minute
                raise RateLimitError("gemini", 60)
            raise ProviderError(f"Gemini generation failed: {error_msg}", "gemini")

class FallbackProvider(BaseProvider):
    """Simple fallback that returns structured errors"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._available = True
    
    def is_available(self) -> bool:
        return True
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        fallback_content = "I apologize, but I'm currently experiencing technical difficulties. Please try your request again in a moment."
        
        structured_output = None
        if request.response_format == "json":
            structured_output = {
                "error": "provider_unavailable",
                "message": fallback_content,
                "retry_recommended": True
            }
            fallback_content = json.dumps(structured_output, indent=2)
        
        return LLMResponse(
            content=fallback_content,
            model_used="fallback",
            provider="fallback",
            response_time=0.1,
            structured_output=structured_output
        )

class ProviderManager:
    def __init__(self):
        self.providers: List[BaseProvider] = []
        self.load_providers()
    
    def load_providers(self):
        """Load providers from config"""
        providers_config = [
            {
                "name": "gemini",
                "type": ProviderType.GEMINI,
                "model": "gemini-1.5-flash",
                "priority": 1
            },
            {
                "name": "fallback",
                "type": ProviderType.FALLBACK,
                "priority": 999  # Always last
            }
        ]
        
        for config in providers_config:
            try:
                if config["type"] == ProviderType.GEMINI:
                    provider = GeminiProvider(config)
                elif config["type"] == ProviderType.FALLBACK:
                    provider = FallbackProvider(config)
                else:
                    continue
                
                self.providers.append(provider)
                logger.info(f"Loaded provider: {config['name']}")
            except Exception as e:
                logger.error(f"Failed to load provider {config['name']}: {e}")
        
        # Sort by priority
        self.providers.sort(key=lambda p: p.config.get("priority", 100))
    
    async def generate_response(self, request: LLMRequest, max_retries: int = 2) -> LLMResponse:
        """Try providers in order with fallbacks"""
        last_error = None
        
        for provider in self.providers:
            if not provider.is_available():
                continue
            
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Trying provider {provider.name} (attempt {attempt + 1})")
                    response = await provider.generate_response(request)
                    logger.info(f"Successfully generated response with {provider.name}")
                    return response
                
                except RateLimitError as e:
                    logger.warning(f"Rate limit hit for {provider.name}: {e}")
                    last_error = e
                    break  # Don't retry rate limits
                
                except ProviderError as e:
                    logger.warning(f"Provider {provider.name} failed (attempt {attempt + 1}): {e}")
                    last_error = e
                    if not e.retryable or attempt >= max_retries:
                        break
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                except Exception as e:
                    logger.error(f"Unexpected error with {provider.name}: {e}")
                    last_error = ProviderError(str(e), provider.name)
                    break
        
        # If we get here, all providers failed
        error_msg = f"All providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise ProviderError(error_msg, "all_providers")
    
    @asynccontextmanager
    async def with_timeout(self, timeout: float = 30.0):
        """Context manager for request timeouts"""
        try:
            yield await asyncio.wait_for(self._inner_context(), timeout=timeout)
        except asyncio.TimeoutError:
            raise ProviderError("Request timeout", "timeout")
    
    async def _inner_context(self):
        return self

# Global provider manager instance
_provider_manager = None

def get_provider_manager() -> ProviderManager:
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager