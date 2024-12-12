"""
LLM Provider Implementation
Provides abstract interface and concrete implementations for LLM integration
"""

import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
import aiohttp
import json
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

class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider"""
        self.config = config
        self.config.validate()

    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Query OpenAI API directly"""
        try:
            api_url = "https://api.openai.com/v1"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.config.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature or self.config.temperature,
                    "max_tokens": max_tokens or self.config.max_tokens
                }

                async with session.post(
                    f"{api_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise RuntimeError(f"OpenAI API error: {error_data}")

                    data = await response.json()
                    return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error querying OpenAI API: {str(e)}")
            raise

    async def batch_query(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """Query OpenAI API with multiple prompts"""
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

class HyperbolicProvider(LLMProvider):
    """Hyperbolic API provider implementation"""

    def __init__(self, config: LLMConfig):
        """Initialize Hyperbolic provider"""
        self.config = config
        self.config.validate()

    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Query Hyperbolic API"""
        try:
            api_url = self.config.api_url.rstrip('/')
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.config.model,
                    "prompt": prompt,  # Hyperbolic uses 'prompt' instead of 'messages'
                    "temperature": temperature or self.config.temperature,
                    "max_tokens": max_tokens or self.config.max_tokens,
                    "stream": False
                }

                async with session.post(
                    f"{api_url}/completions",  # Hyperbolic endpoint
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise RuntimeError(f"Error code: {response.status} - {error_data}")

                    data = await response.json()
                    return data["choices"][0]["text"]

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

class MockProvider(LLMProvider):
    """Mock LLM provider for testing"""

    def __init__(self, config: LLMConfig):
        """Initialize mock provider"""
        self.config = config

    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Return mock response for testing"""
        return json.dumps({
            "decision": True,
            "confidence": 0.85,
            "reasoning": "Market conditions are favorable with low risk. Basic functionality test with minimal exposure."
        })

    async def batch_query(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """Return mock responses for testing"""
        return [await self.query(prompt) for prompt in prompts]

def create_llm_provider(config: Optional[LLMConfig] = None) -> LLMProvider:
    """Create LLM provider from config or environment variables"""
    if not config:
        # Load from environment
        config = LLMConfig(
            provider=os.getenv('LLM_PROVIDER', 'mock'),  # Default to mock for testing
            api_key=os.getenv('LLM_API_KEY', 'mock_key'),
            model=os.getenv('LLM_MODEL', 'mock-model'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
            api_url=os.getenv('HYPERBOLIC_API_URL')
        )

    config.validate()

    provider = config.provider.lower()
    if provider == 'hyperbolic':
        return HyperbolicProvider(config)
    elif provider == 'openai':
        return OpenAIProvider(config)
    elif provider == 'mock':
        return MockProvider(config)  # Add mock provider support
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
