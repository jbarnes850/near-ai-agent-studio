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
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    api_key: str
    model: str = "deepseek-ai/DeepSeek-V3"
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

    async def close(self) -> None:
        """Clean up resources."""
        pass

class HyperbolicProvider(LLMProvider):
    """Hyperbolic API provider implementation using OpenAI SDK"""

    def __init__(self, config: LLMConfig):
        """Initialize Hyperbolic provider"""
        self.config = config
        self.config.validate()
        
        # Initialize OpenAI client with Hyperbolic configuration
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.api_url
        )

    async def query(self, prompt: str, expect_json: bool = False) -> str:
        """Query the LLM provider with a prompt."""
        try:
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.api_url + "/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.model,
                        "messages": [
                            {"role": "system", "content": self.config.system_prompt or "You are a helpful AI assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens,
                        "stream": False,
                        "response_format": {"type": "json_object"} if expect_json else None
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise RuntimeError(f"API request failed: {response.status} - {error_data.get('error', {}).get('message', 'Unknown error')}")
                    
                    data = await response.json()
                    if "choices" not in data:
                        raise RuntimeError("Invalid API response format")
                    content = data["choices"][0]["message"]["content"].strip()
                    
                    # If JSON is expected, validate and parse
                    if expect_json:
                        try:
                            json.loads(content)  # Validate JSON
                            return content
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON response: {content}")
                            raise RuntimeError(f"Invalid JSON response from LLM: {str(e)}")
                    
                    # For non-JSON responses, return as is
                    return content
                    
        except Exception as e:
            logger.error(f"Error querying API: {str(e)}")
            raise

    async def stream(self, prompt: str):
        """Stream responses from the LLM provider."""
        try:
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.api_url + "/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.model,
                        "messages": [
                            {"role": "system", "content": self.config.system_prompt or "You are a helpful AI assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens,
                        "stream": True
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise RuntimeError(f"API request failed: {response.status} - {error_data.get('error', {}).get('message', 'Unknown error')}")
                    
                    # Handle streaming response
                    async for line in response.content:
                        if line:
                            try:
                                line = line.decode('utf-8').strip()
                                if line.startswith('data: '):
                                    data = json.loads(line[6:])
                                    if data.get('choices') and data['choices'][0].get('delta', {}).get('content'):
                                        chunk = data['choices'][0]['delta']['content']
                                        yield chunk
                            except Exception as e:
                                logger.error(f"Error parsing stream chunk: {str(e)}")
                                continue
                    
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
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

    async def close(self) -> None:
        """Clean up resources."""
        # OpenAI client doesn't need explicit cleanup
        pass

def create_llm_provider(config: LLMConfig) -> LLMProvider:
    """Create an LLM provider based on configuration."""
    if config.provider.lower() == "openai":
        return OpenAIProvider(config)
    elif config.provider.lower() == "hyperbolic":
        return HyperbolicProvider(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")

