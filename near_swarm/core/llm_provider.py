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
                messages = [{"role": "user", "content": "Say 'Connected' if you can hear me."}]
                temp = 0.1
                tokens = 10
                response_format = None
            else:
                # Enhanced system prompt for more reliable JSON responses
                system_prompt = """You are a specialized NEAR Protocol trading agent.
You must respond ONLY with valid JSON in the following format:
{
    "decision": true/false,     // Boolean: true to approve, false to reject
    "confidence": 0.0 to 1.0,   // Number: your confidence level
    "reasoning": "string"       // String: your detailed analysis
}

Example response:
{
    "decision": false,
    "confidence": 0.85,
    "reasoning": "Market volatility is high and price trend is downward..."
}

Focus your analysis on:
1. Market conditions and trends
2. Risk factors and exposure
3. Network conditions and costs
4. Historical patterns
5. Technical indicators

DO NOT include any text outside the JSON object.
DO NOT include comments in the JSON.
DO NOT include any explanatory text.
ENSURE all values have the correct data types."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                temp = temperature or self.config.temperature
                tokens = max_tokens or self.config.max_tokens
                response_format = {"type": "json_object"}

            # Make API call
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                response_format=response_format
            )

            content = completion.choices[0].message.content.strip()

            # For test prompts, return as is
            if "test_connection" in prompt.lower():
                return "OK" if "connected" in content.lower() else "Failed"

            # For regular prompts, validate JSON response
            try:
                # Remove any non-JSON text that might be present
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    content = content[json_start:json_end]
                
                parsed = json.loads(content)
                
                # Validate data types and ranges
                if not isinstance(parsed.get("decision"), bool):
                    raise ValueError("Decision must be a boolean")
                
                confidence = parsed.get("confidence")
                if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                    raise ValueError("Confidence must be a number between 0 and 1")
                
                if not isinstance(parsed.get("reasoning"), str) or not parsed.get("reasoning"):
                    raise ValueError("Reasoning must be a non-empty string")
                
                # Return the cleaned and validated JSON
                return json.dumps({
                    "decision": parsed["decision"],
                    "confidence": float(confidence),
                    "reasoning": parsed["reasoning"]
                })
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {content}")
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            except Exception as e:
                logger.error(f"Error validating response: {content}")
                raise ValueError(f"Error validating LLM response: {str(e)}")

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

