"""API models for openmcp."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    """Request model for tool calls."""

    tool_name: str = Field(description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )
    session_id: Optional[str] = Field(None, description="Session ID for stateful tools")


class ToolCallResponse(BaseModel):
    """Response model for tool calls."""

    success: bool = Field(description="Whether the call was successful")
    result: Dict[str, Any] = Field(description="Tool call result")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    error: Optional[str] = Field(None, description="Error message if failed")


class ServiceInfo(BaseModel):
    """Service information model."""

    name: str = Field(description="Service name")
    status: str = Field(description="Service status")
    tools: List[str] = Field(description="Available tools")
    config: Dict[str, Any] = Field(description="Service configuration")


class APIKeyRequest(BaseModel):
    """Request model for creating API keys."""

    name: str = Field(description="API key name")
    expires_days: Optional[int] = Field(None, description="Expiration in days")
    permissions: Optional[Dict[str, bool]] = Field(
        None, description="Service permissions"
    )


class APIKeyResponse(BaseModel):
    """Response model for API key creation."""

    api_key: str = Field(description="Generated API key")
    name: str = Field(description="API key name")
    expires_days: Optional[int] = Field(None, description="Expiration in days")


class ServiceListResponse(BaseModel):
    """Response model for service listing."""

    available_services: List[str] = Field(description="Available service classes")
    running_services: List[str] = Field(description="Currently running services")
    service_details: Dict[str, ServiceInfo] = Field(description="Detailed service info")


class ToolListResponse(BaseModel):
    """Response model for tool listing."""

    service: str = Field(description="Service name")
    tools: List[Dict[str, Any]] = Field(description="Available tools with schemas")
