"""Configuration management for openmcp."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=9000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")


class AuthConfig(BaseModel):
    """Authentication configuration."""

    secret_key: str = Field(description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    allow_localhost: bool = Field(
        default=True, description="Allow localhost connections without API key"
    )
    mock_api_key: str = Field(
        default="openmcp-localhost-auth", description="Mock API key for testing"
    )


class MCPServiceConfig(BaseModel):
    """MCP service configuration."""

    name: str = Field(description="Service name")
    enabled: bool = Field(default=True, description="Whether service is enabled")
    config: Dict = Field(default_factory=dict, description="Service-specific config")


class Config(BaseModel):
    """Main configuration class."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    auth: AuthConfig = Field(description="Authentication configuration")
    services: List[MCPServiceConfig] = Field(
        default_factory=list, description="MCP services configuration"
    )

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from file."""
        if config_path is None:
            config_path = Path("config.yaml")

        if not config_path.exists():
            # Create default config
            return cls.create_default()

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    @classmethod
    def create_default(cls) -> "Config":
        """Create default configuration."""
        # Generate a default secret key from environment or create one
        secret_key = os.getenv("OPENMCP_SECRET_KEY", "your-secret-key-change-this")

        return cls(
            auth=AuthConfig(secret_key=secret_key),
            services=[
                MCPServiceConfig(
                    name="browseruse",
                    enabled=True,
                    config={"headless": True, "timeout": 30, "max_sessions": 5},
                )
            ],
        )

    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file."""
        if config_path is None:
            config_path = Path("config.yaml")

        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
