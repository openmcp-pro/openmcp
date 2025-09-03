"""Main openmcp server implementation."""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional

import structlog
import uvicorn
from fastapi import FastAPI

from .auth import AuthManager
from .config import Config
from .mcp_registry import MCPRegistry
from ..api.routes import create_api_router
from ..services import BrowseruseService

logger = structlog.get_logger(__name__)


class OpenMCPServer:
    """Main openmcp server class."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = Config.from_file(config_path)
        self.auth_manager = AuthManager(self.config.auth)
        self.mcp_registry = MCPRegistry()
        self.app: Optional[FastAPI] = None
        
        # Register available services
        self._register_services()
    
    def _register_services(self) -> None:
        """Register available MCP services."""
        self.mcp_registry.register_service_class("browseruse", BrowseruseService)
    
    async def start_services(self) -> None:
        """Start configured MCP services."""
        for service_config in self.config.services:
            if service_config.enabled:
                success = await self.mcp_registry.start_service(
                    service_config.name, 
                    service_config.config
                )
                if success:
                    logger.info("Started service", service=service_config.name)
                else:
                    logger.error("Failed to start service", service=service_config.name)
    
    async def stop_services(self) -> None:
        """Stop all MCP services."""
        await self.mcp_registry.stop_all_services()
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """FastAPI lifespan context manager."""
        # Startup
        logger.info("Starting openmcp server")
        await self.start_services()
        
        # Print API keys for easy access
        api_keys = self.auth_manager.list_api_keys()
        if api_keys:
            logger.info("Available API keys:")
            for key, key_obj in api_keys.items():
                logger.info(f"  {key_obj.name}: {key}")
        
        yield
        
        # Shutdown
        logger.info("Shutting down openmcp server")
        await self.stop_services()
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="openmcp",
            description="A collection of optimized MCP services for AI Agents",
            version="0.1.0",
            lifespan=self.lifespan
        )
        
        # Include API routes
        api_router = create_api_router(self.auth_manager, self.mcp_registry)
        app.include_router(api_router, prefix="/api/v1")
        
        # Health check endpoint
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "services": {
                    name: self.mcp_registry.get_service_status(name)
                    for name in self.mcp_registry.list_available_services()
                }
            }
        
        # Root endpoint
        @app.get("/")
        async def root():
            return {
                "message": "Welcome to openmcp - Optimized MCP services for AI Agents",
                "version": "0.1.0",
                "available_services": self.mcp_registry.list_available_services(),
                "running_services": self.mcp_registry.list_services()
            }
        
        self.app = app
        return app
    
    def run(
        self, 
        host: Optional[str] = None, 
        port: Optional[int] = None,
        **kwargs
    ) -> None:
        """Run the server."""
        app = self.create_app()
        
        host = host or self.config.server.host
        port = port or self.config.server.port
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=self.config.server.log_level.lower(),
            **kwargs
        )
    
    async def run_async(
        self, 
        host: Optional[str] = None, 
        port: Optional[int] = None
    ) -> None:
        """Run the server asynchronously."""
        app = self.create_app()
        
        host = host or self.config.server.host
        port = port or self.config.server.port
        
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level=self.config.server.log_level.lower()
        )
        
        server = uvicorn.Server(config)
        await server.serve()
