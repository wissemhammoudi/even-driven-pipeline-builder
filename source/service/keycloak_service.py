from source.service.keycloak.main_service import KeycloakService
import asyncio

__all__ = ['KeycloakService']

_keycloak_service_instance = None
_lock = asyncio.Lock()

async def get_keycloak_service() -> KeycloakService:
    global _keycloak_service_instance
    
    async with _lock:
        if _keycloak_service_instance is None:
            _keycloak_service_instance = KeycloakService()
            await _keycloak_service_instance.__aenter__()
        elif not _keycloak_service_instance.session:
            await _keycloak_service_instance.__aenter__()
    
    return _keycloak_service_instance

def get_keycloak_service_sync() -> KeycloakService:
    global _keycloak_service_instance
    if _keycloak_service_instance is None:
        _keycloak_service_instance = KeycloakService()
    return _keycloak_service_instance

async def create_keycloak_service() -> KeycloakService:
    service = KeycloakService()
    await service.initialize()
    return service

async def close_keycloak_service(service: KeycloakService):
    if service:
        await service.close()

async def cleanup_keycloak_service():
    global _keycloak_service_instance
    if _keycloak_service_instance:
        await _keycloak_service_instance.__aexit__(None, None, None)
        _keycloak_service_instance = None
