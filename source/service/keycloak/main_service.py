import aiohttp
from typing import Dict, Optional, Any
from source.config.config import keycloak_config, application_user_init_config
from .setup_service import KeycloakSetupService
from .user_service import KeycloakUserService
from .auth_service import KeycloakAuthService
from .connection_service import KeycloakConnectionService

class KeycloakService:
    def __init__(self):
        self.config = keycloak_config
        self.admin_token = None
        self.session = None
        
    async def __aenter__(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the service"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_services(self):
        """Get all the focused service instances"""
        if not self.session:
            raise RuntimeError("KeycloakService session not initialized. Use async context manager.")
        
        setup_service = KeycloakSetupService(self.session)
        user_service = KeycloakUserService(self.session, setup_service)
        auth_service = KeycloakAuthService(self.session)
        connection_service = KeycloakConnectionService(self.session)
        return setup_service, user_service, auth_service, connection_service
    
    async def test_connection(self) -> Dict[str, Any]:
        try:
            _, _, _, connection_service = self._get_services()
            return await connection_service.test_connection()
        except Exception as e:
            raise Exception(f"Failed to test Keycloak connection: {str(e)}")
    
    async def wait_for_ready(self, max_attempts: int = 15, delay: float = 3.0) -> bool:
        try:
            _, _, _, connection_service = self._get_services()
            return await connection_service.wait_for_ready(max_attempts, delay)
        except Exception as e:
            raise Exception(f"Failed to wait for Keycloak to be ready: {str(e)}")
    
    async def check_and_create_realm(self) -> bool:
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.check_and_create_realm()
        except Exception as e:
            raise Exception(f"Failed to check and create Keycloak realm: {str(e)}")
    
    async def create_client(self) -> bool:
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.create_client()
        except Exception as e:
            raise Exception(f"Failed to create Keycloak client: {str(e)}")
    
    async def create_roles(self) -> bool:
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.create_roles()
        except Exception as e:
            raise Exception(f"Failed to create Keycloak roles: {str(e)}")
    
    async def create_admin_user(self) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_admin_user()
        except Exception as e:
            raise Exception(f"Failed to create admin user in Keycloak: {str(e)}")
    
    async def create_local_admin_user(self) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_local_admin_user()
        except Exception as e:
            raise Exception(f"Failed to create local admin user: {str(e)}")
    
    async def setup_keycloak(self) -> Dict[str, Any]:
        try:

            if not await self.create_client():
                return {"success": False, "message": "Failed to create client"}
            
            if not await self.create_roles():
                return {"success": False, "message": "Failed to create roles"}
            
            if not await self.create_admin_user():
                return {"success": False, "message": "Failed to create admin user in Keycloak"}
            
            if not await self.create_local_admin_user():
                return {"success": False, "message": "Failed to create admin user in local database"}
            
            return {"success": True, "message": "Keycloak setup completed successfully"}
            
        except Exception as e:
            raise Exception(f"Failed to setup Keycloak: {str(e)}")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.authenticate_user(username, password)
        except Exception as e:
            raise Exception(f"Failed to authenticate user '{username}': {str(e)}")
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.verify_token(token)
        except Exception as e:
            raise Exception(f"Failed to verify token: {str(e)}")
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.get_user_info(token)
        except Exception as e:
            raise Exception(f"Failed to get user info from token: {str(e)}")
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.refresh_token(refresh_token)
        except Exception as e:
            raise Exception(f"Failed to refresh token: {str(e)}")
    
    async def ensure_admin_user_exists(self) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            
            admin_token = await user_service.setup_service.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={application_user_init_config.admin_username}"
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        keycloak_exists = True
                    else:
                        keycloak_exists = await user_service.create_admin_user()
                else:
                    keycloak_exists = False
            
            local_exists = await user_service.create_local_admin_user()
            
            return keycloak_exists and local_exists
            
        except Exception as e:
            raise Exception(f"Failed to ensure admin user exists: {str(e)}")
    
    async def create_demo_users(self) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_demo_users()
        except Exception as e:
            raise Exception(f"Failed to create demo users: {str(e)}")
    
    async def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str, role: str) -> Optional[str]:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_user(username, email, first_name, last_name, password, role)
        except Exception as e:
            raise Exception(f"Failed to create user '{username}': {str(e)}")
    
    async def update_user(self, user_id: str, username: str = None, email: str = None, first_name: str = None, last_name: str = None, role: str = None) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.update_user(user_id, username, email, first_name, last_name, role)
        except Exception as e:
            raise Exception(f"Failed to update user '{user_id}': {str(e)}")
    
    async def delete_user(self, user_id: str) -> bool:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.delete_user(user_id)
        except Exception as e:
            raise Exception(f"Failed to delete user '{user_id}': {str(e)}")
    
    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.get_user_id_by_username(username)
        except Exception as e:
            raise Exception(f"Failed to get user ID for username '{username}': {str(e)}")