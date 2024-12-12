"""
LLM Provider Implementation
Provides abstract interface and concrete implementations for LLM integration
"""

import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
import openai
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    api_url: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration"""
        if not self.provider:
            raise ValueError("LLM provider is required")
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.model:
            raise ValueError("Model name is required")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("Temperature must be between 0 and 1")
        if self.max_tokens < 1:
            raise ValueError("Max tokens must be positive")

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Query the LLM with a prompt"""
        pass

    @abstractmethod
    async def batch_query(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """Query the LLM with multiple prompts"""
        pass

class HyperbolicProvider(LLMProvider):
    """Hyperbolic AI provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize Hyperbolic provider"""
        self.config = config
        self.config.validate()

        # Configure OpenAI client for Hyperbolic
        openai.api_key = config.api_key
        if config.api_url:
            openai.api_base = config.api_url

    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Query Hyperbolic API"""
        try:
            response = await openai.ChatCompletion.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error querying Hyperbolic API: {str(e)}")
            raise

    async def batch_query(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """Query Hyperbolic API with multiple prompts"""
        try:
            responses = []
            for prompt in prompts:
                response = await self.query(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                responses.append(response)
            return responses

        except Exception as e:
            logger.error(f"Error in batch query: {str(e)}")
            raise

def create_llm_provider(config: Optional[LLMConfig] = None) -> LLMProvider:
    """Create LLM provider from config or environment variables"""
    if not config:
        # Load from environment
        config = LLMConfig(
            provider=os.getenv('LLM_PROVIDER', 'hyperbolic'),
            api_key=os.getenv('LLM_API_KEY', ''),
            model=os.getenv('LLM_MODEL', 'meta-llama/Llama-3.3-70B-Instruct'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
            api_url=os.getenv('HYPERBOLIC_API_URL')
        )

    config.validate()

    if config.provider.lower() == 'hyperbolic':
        return HyperbolicProvider(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
