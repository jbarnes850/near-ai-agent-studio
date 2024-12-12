"""
Tests for LLM provider implementation
"""

import pytest
from near_swarm.core.llm_provider import (
    LLMConfig,
    create_llm_provider,
    HyperbolicProvider
)

def test_llm_config_validation():
    """Test LLM configuration validation"""
    # Valid config
    config = LLMConfig(
        provider="hyperbolic",
        api_key="test_key",
        model="test_model",
        temperature=0.7,
        max_tokens=2000
    )
    config.validate()  # Should not raise

    # Invalid temperature
    with pytest.raises(ValueError):
        LLMConfig(
            provider="hyperbolic",
            api_key="test_key",
            model="test_model",
            temperature=1.5
        ).validate()

    # Missing required fields
    with pytest.raises(ValueError):
        LLMConfig(
            provider="",
            api_key="test_key",
            model="test_model"
        ).validate()

@pytest.mark.asyncio
async def test_hyperbolic_provider():
    """Test Hyperbolic provider implementation"""
    config = LLMConfig(
        provider="hyperbolic",
        api_key="test_key",
        model="test_model"
    )

    provider = HyperbolicProvider(config)
    assert isinstance(provider, HyperbolicProvider)

def test_create_llm_provider():
    """Test LLM provider factory function"""
    config = LLMConfig(
        provider="hyperbolic",
        api_key="test_key",
        model="test_model"
    )

    provider = create_llm_provider(config)
    assert isinstance(provider, HyperbolicProvider)

    # Test invalid provider
    with pytest.raises(ValueError):
        create_llm_provider(LLMConfig(
            provider="invalid",
            api_key="test_key",
            model="test_model"
        ))
