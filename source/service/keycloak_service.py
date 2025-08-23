from source.service.keycloak.main_service import KeycloakService

# For backward compatibility
__all__ = ['KeycloakService']

# Global instance for dependency injection
_keycloak_service_instance = None

def get_keycloak_service() -> KeycloakService:
    """Get or create a KeycloakService instance"""
    global _keycloak_service_instance
    if _keycloak_service_instance is None:
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
