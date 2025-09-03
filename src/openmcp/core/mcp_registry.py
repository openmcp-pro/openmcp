"""MCP service registry and management."""

import asyncio
from typing import Dict, List, Optional, Type

import structlog

from ..services.base import BaseMCPService

logger = structlog.get_logger(__name__)


class MCPRegistry:
    """Registry for managing MCP services."""
    
    def __init__(self):
        self.services: Dict[str, BaseMCPService] = {}
        self.service_classes: Dict[str, Type[BaseMCPService]] = {}
    
    def register_service_class(
        self, 
        name: str, 
        service_class: Type[BaseMCPService]
    ) -> None:
        """Register a service class."""
        self.service_classes[name] = service_class
        logger.info("Registered service class", service=name)
    
    async def start_service(self, name: str, config: dict) -> bool:
        """Start a service instance."""
        if name in self.services:
            logger.warning("Service already running", service=name)
            return False
        
        if name not in self.service_classes:
            logger.error("Service class not registered", service=name)
            return False
        
        try:
            service_class = self.service_classes[name]
            service = service_class(config)
            await service.start()
            self.services[name] = service
            logger.info("Started service", service=name)
            return True
        except Exception as e:
            logger.error("Failed to start service", service=name, error=str(e))
            return False
    
    async def stop_service(self, name: str) -> bool:
        """Stop a service instance."""
        if name not in self.services:
            logger.warning("Service not running", service=name)
            return False
        
        try:
            service = self.services[name]
            await service.stop()
            del self.services[name]
            logger.info("Stopped service", service=name)
            return True
        except Exception as e:
            logger.error("Failed to stop service", service=name, error=str(e))
            return False
    
    async def restart_service(self, name: str, config: dict) -> bool:
        """Restart a service."""
        if name in self.services:
            await self.stop_service(name)
        return await self.start_service(name, config)
    
    def get_service(self, name: str) -> Optional[BaseMCPService]:
        """Get a service instance."""
        return self.services.get(name)
    
    def list_services(self) -> List[str]:
        """List all running services."""
        return list(self.services.keys())
    
    def list_available_services(self) -> List[str]:
        """List all available service classes."""
        return list(self.service_classes.keys())
    
    async def stop_all_services(self) -> None:
        """Stop all running services."""
        tasks = []
        for name in list(self.services.keys()):
            tasks.append(self.stop_service(name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_service_status(self, name: str) -> dict:
        """Get service status."""
        if name not in self.services:
            return {"status": "stopped", "available": name in self.service_classes}
        
        service = self.services[name]
        return {
            "status": "running",
            "available": True,
            "health": service.health_check() if hasattr(service, "health_check") else "unknown"
        }
