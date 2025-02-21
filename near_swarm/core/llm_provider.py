"""
LLM Provider Implementation
Provides abstract interface and concrete implementations for LLM integration
"""

import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import logging
import json
from dataclasses import dataclass
import openai
from openai import OpenAI
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    api_key: str
    model: str = "meta-llama/Llama-3.3-70B-Instruct"  # Default model for Hyperbolic
    temperature: float = 0.7
    max_tokens: int = 2000
    api_url: str = "https://api.hyperbolic.xyz/v1"
    system_prompt: Optional[str] = None

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
        if not self.api_url:
            self.api_url = "https://api.hyperbolic.xyz/v1"
        # Normalize provider name
        self.provider = self.provider.lower().strip()

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self):
        self._client = None
    
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

    async def close(self) -> None:
        """Clean up resources."""
        # OpenAI client doesn't need explicit cleanup
        pass

class HyperbolicProvider(LLMProvider):
    """Hyperbolic API provider implementation using OpenAI SDK"""

    def __init__(self, config: LLMConfig):
        """Initialize Hyperbolic provider"""
        super().__init__()
        self.config = config
        self.config.validate()
        
        # Initialize OpenAI client with Hyperbolic configuration
        self._client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_url
        )

    async def query(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """Query the LLM provider with a prompt."""
        try:
            chat_completion = self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt or "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
            
            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error querying Hyperbolic API: {str(e)}")
            raise

    async def batch_query(
        self,
        prompts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> List[str]:
        """Query with multiple prompts in parallel."""
        try:
            results = []
            for prompt in prompts:
                result = await self.query(prompt, temperature=temperature, max_tokens=max_tokens)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error in batch query: {str(e)}")
            raise

def create_llm_provider(config: LLMConfig) -> LLMProvider:
    """Create LLM provider instance based on configuration."""
    config.validate()
    provider = config.provider.lower().strip()
    if provider == "hyperbolic":
        return HyperbolicProvider(config)
    raise ValueError(f"Unsupported LLM provider '{provider}'. Currently supported: hyperbolic")

