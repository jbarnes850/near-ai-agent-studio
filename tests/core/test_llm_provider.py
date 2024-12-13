"""
Tests for LLM provider implementation
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from near_swarm.core.llm_provider import (
    LLMConfig,
    create_llm_provider,
    MockProvider
)

@pytest.fixture
def mock_config():
    """Create mock config for testing."""
    return LLMConfig(
        provider="mock",
        api_key="test_key",
        model="test_model"
    )

@pytest.mark.asyncio
async def test_mock_llm_provider(mock_config):
    """Test mock LLM provider."""
    provider = create_llm_provider(mock_config)
    
    test_prompt = """You are a NEAR Protocol trading agent. 
    Evaluate this simple trade proposal and respond in JSON format:
    {
        "decision": true/false,
        "confidence": float between 0-1,
        "reasoning": "your explanation"
    }
    
    Proposal: Buy 10 NEAR at current market price."""
    
    try:
        response = await provider.query(test_prompt)
        print(f"\nLLM Response: {response}")
        
        # Validate response format
        data = json.loads(response)
        assert isinstance(data["decision"], bool), "Decision must be boolean"
        assert 0 <= data["confidence"] <= 1, "Confidence must be between 0 and 1"
        assert isinstance(data["reasoning"], str), "Reasoning must be string"
        assert len(data["reasoning"]) > 0, "Reasoning cannot be empty"
            
    finally:
        if hasattr(provider, 'close'):
            await provider.close()

@pytest.mark.asyncio
async def test_batch_query(mock_config):
    """Test batch query functionality."""
    provider = create_llm_provider(mock_config)
    
    prompts = [
        "Test prompt 1",
        "Test prompt 2"
    ]
    
    try:
        responses = await provider.batch_query(prompts)
        assert len(responses) == 2, "Should get two responses"
        assert all(isinstance(r, str) for r in responses), "All responses should be strings"
        assert all(len(r) > 0 for r in responses), "No empty responses"
    finally:
        if hasattr(provider, 'close'):
            await provider.close()

@pytest.mark.asyncio
@patch('aiohttp.ClientSession')
async def test_hyperbolic_provider_integration(mock_session):
    """Test Hyperbolic provider with mocked HTTP calls."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "decision": "buy",
                    "confidence": 0.85,
                    "reasoning": ["Test reasoning point 1", "Test reasoning point 2"]
                })
            }
        }]
    }
    
    mock_session.return_value.post.return_value.__aenter__.return_value = mock_response
    
    config = LLMConfig(
        provider="hyperbolic",
        api_key="test_key",
        model="test_model",
        api_url="https://api.hyperbolic.xyz/v1/chat/completions"
    )
    
    provider = create_llm_provider(config)
    response = await provider.query("Test prompt")
    
    data = json.loads(response)
    assert isinstance(data["decision"], (bool, str))
    assert isinstance(data["confidence"], float)
    assert isinstance(data["reasoning"], (str, list))

@pytest.mark.asyncio
async def test_hyperbolic_direct_api():
    """Test direct Hyperbolic API connection."""
    config = LLMConfig(
        provider="hyperbolic",
        api_key="your_test_key",
        model="meta-llama/Llama-3.3-70B-Instruct",
        api_url="https://api.hyperbolic.xyz/v1/chat/completions"
    )
    
    provider = create_llm_provider(config)
    try:
        response = await provider.query(
            "You are a NEAR Protocol trading agent. Analyze this trade: Buy 10 NEAR at current price."
        )
        
        # Verify JSON response format
        data = json.loads(response)
        assert "decision" in data
        assert "confidence" in data
        assert "reasoning" in data
        
    finally:
        await provider.close()
