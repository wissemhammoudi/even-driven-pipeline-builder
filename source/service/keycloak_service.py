from source.service.keycloak.main_service import KeycloakService
import asyncio
import logging

# Configure logging
logger = logging.getLogger(__name__)

# For backward compatibility
__all__ = ['KeycloakService']

# Global instance for dependency injection
_keycloak_service_instance = None
_lock = asyncio.Lock()

async def get_keycloak_service() -> KeycloakService:
    """Get or create a KeycloakService instance with proper async context"""
    global _keycloak_service_instance
    
    async with _lock:
        if _keycloak_service_instance is None:
            logger.info("Initializing KeycloakService...")
            _keycloak_service_instance = KeycloakService()
            await _keycloak_service_instance.__aenter__()
            logger.info("KeycloakService initialized successfully")
        elif not _keycloak_service_instance.session:
            logger.info("Reinitializing KeycloakService session...")
            await _keycloak_service_instance.__aenter__()
            logger.info("KeycloakService session reinitialized")
    
    return _keycloak_service_instance

def get_keycloak_service_sync() -> KeycloakService:
    """Get KeycloakService instance without async context (for backward compatibility)"""
    global _keycloak_service_instance
    if _keycloak_service_instance is None:
        logger.warning("KeycloakService not initialized. Use get_keycloak_service() for async operations.")
        _keycloak_service_instance = KeycloakService()
    return _keycloak_service_instance

async def create_keycloak_service() -> KeycloakService:
    """Create a new KeycloakService instance with proper async context"""
    service = KeycloakService()
    await service.__aenter__()
    return service

async def close_keycloak_service(service: KeycloakService):
    """Close a KeycloakService instance"""
    if service:
        await service.__aexit__(None, None, None)

async def cleanup_keycloak_service():
    """Cleanup the global KeycloakService instance"""
    global _keycloak_service_instance
    if _keycloak_service_instance:
        await _keycloak_service_instance.__aexit__(None, None, None)
        _keycloak_service_instance = None
        logger.info("KeycloakService cleaned up")
