"""
Configuration schemas for NEAR Swarm Intelligence
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class LLMSettings(BaseModel):
    """LLM configuration settings"""
    provider: str = Field(..., description="LLM provider name")
    model: str = Field(..., description="Model name/version")
    api_key: str = Field(..., description="API key for the provider")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: int = Field(1000, description="Maximum tokens per request")
    api_url: Optional[str] = Field(None, description="Custom API endpoint URL")
    system_prompt: Optional[str] = Field(None, description="Default system prompt")

class PluginSettings(BaseModel):
    """Plugin-specific settings"""
    name: str = Field(..., description="Plugin name")
    role: str = Field(..., description="Plugin role in the swarm")
    capabilities: List[str] = Field(default_factory=list, description="Plugin capabilities")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom plugin settings")

class AgentConfig(BaseModel):
    """Main agent configuration"""
    name: str = Field(..., description="Agent name")
    llm: Optional[LLMSettings] = Field(None, description="LLM configuration")
    plugins: List[PluginSettings] = Field(default_factory=list, description="Plugin configurations")
    environment: str = Field("development", description="Deployment environment")
    log_level: str = Field("INFO", description="Logging level")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom agent settings")

    class Config:
        """Pydantic config"""
        validate_assignment = True
        extra = "forbid" 