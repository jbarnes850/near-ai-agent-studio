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

    async def query(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Query Hyperbolic API using OpenAI SDK."""
        try:
            # Check if this is a test prompt
            if "test_connection" in prompt.lower():
                # For test prompts, use a simpler format
                messages = [{"role": "user", "content": "Say 'Connected' if you can hear me."}]
                temp = 0.1  # Lower temperature for test
                tokens = 10  # Fewer tokens for test
                response_format = None
            else:
                # Use provided system prompt or default
                system_prompt = self.config.system_prompt or """You are a specialized NEAR Protocol trading agent.
Your responses must always be in valid JSON format with the following structure:
{
    "decision": boolean,      // Your decision to approve or reject
    "confidence": float,      // Confidence level between 0.0 and 1.0
    "reasoning": string       // Detailed explanation of your decision
}

Consider all provided market context in your analysis. Focus on:
1. Current market conditions and trends
2. Risk factors and exposure levels
3. Network conditions and gas costs
4. Historical patterns and volatility
5. Technical indicators and metrics

Always provide thorough reasoning for your decisions."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                temp = temperature or self.config.temperature
                tokens = max_tokens or self.config.max_tokens
                response_format = {"type": "json_object"}

            # Make the API call using the OpenAI SDK
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                response_format=response_format
            )

            content = completion.choices[0].message.content

            # For test prompts, return as is
            if "test_connection" in prompt.lower():
                return "OK" if "connected" in content.lower() else "Failed"

            # For regular prompts, validate JSON response
            try:
                parsed = json.loads(content)
                required_fields = ["decision", "confidence", "reasoning"]
                if not all(field in parsed for field in required_fields):
                    raise ValueError("Missing required fields in response")
                if not isinstance(parsed["decision"], bool):
                    raise ValueError("Decision must be a boolean")
                if not isinstance(parsed["confidence"], (int, float)):
                    raise ValueError("Confidence must be a number")
                if not isinstance(parsed["reasoning"], str):
                    raise ValueError("Reasoning must be a string")
                return content
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON response from LLM")

        except Exception as e:
            logger.error(f"Error querying API: {str(e)}")
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

