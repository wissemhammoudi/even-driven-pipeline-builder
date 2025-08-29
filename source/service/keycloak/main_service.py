import aiohttp
from typing import Dict, Optional, Any
from source.config.config import keycloak_config, application_user_init_config
from .setup_service import KeycloakSetupService
from .user_service import KeycloakUserService
from .auth_service import KeycloakAuthService
from .connection_service import KeycloakConnectionService
import logging

# Configure logging
logger = logging.getLogger(__name__)

class KeycloakService:
    def __init__(self):
        self.config = keycloak_config
        self.admin_token = None
        self.session = None
        
    async def __aenter__(self):
        """Initialize the service with aiohttp session"""
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
        """Test connection to Keycloak server"""
        try:
            _, _, _, connection_service = self._get_services()
            return await connection_service.test_connection()
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {"reachable": False, "error": str(e)}
    
    async def wait_for_ready(self, max_attempts: int = 15, delay: float = 3.0) -> bool:
        """Wait for Keycloak to be ready"""
        try:
            _, _, _, connection_service = self._get_services()
            return await connection_service.wait_for_ready(max_attempts, delay)
        except Exception as e:
            logger.error(f"Wait for ready failed: {str(e)}")
            return False
    
    async def check_and_create_realm(self) -> bool:
        """Check and create realm if it doesn't exist"""
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.check_and_create_realm()
        except Exception as e:
            logger.error(f"Realm check/create failed: {str(e)}")
            return False
    
    async def create_client(self) -> bool:
        """Create client in Keycloak"""
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.create_client()
        except Exception as e:
            logger.error(f"Client creation failed: {str(e)}")
            return False
    
    async def create_roles(self) -> bool:
        """Create roles in Keycloak"""
        try:
            setup_service, _, _, _ = self._get_services()
            return await setup_service.create_roles()
        except Exception as e:
            logger.error(f"Role creation failed: {str(e)}")
            return False
    
    async def create_admin_user(self) -> bool:
        """Create admin user in Keycloak"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_admin_user()
        except Exception as e:
            logger.error(f"Admin user creation failed: {str(e)}")
            return False
    
    async def create_local_admin_user(self) -> bool:
        """Create admin user in local database"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_local_admin_user()
        except Exception as e:
            logger.error(f"Local admin user creation failed: {str(e)}")
            return False
    
    async def setup_keycloak(self) -> Dict[str, Any]:
        """Complete Keycloak setup"""
        try:
            logger.info("Starting Keycloak setup...")
            
            if not await self.create_client():
                logger.error("Failed to create client")
                return {"success": False, "message": "Failed to create client"}
            
            if not await self.create_roles():
                logger.error("Failed to create roles")
                return {"success": False, "message": "Failed to create roles"}
            
            if not await self.create_admin_user():
                logger.error("Failed to create admin user in Keycloak")
                return {"success": False, "message": "Failed to create admin user in Keycloak"}
            
            if not await self.create_local_admin_user():
                logger.error("Failed to create admin user in local database")
                return {"success": False, "message": "Failed to create admin user in local database"}
            
            logger.info("Keycloak setup completed successfully")
            return {"success": True, "message": "Keycloak setup completed successfully"}
            
        except Exception as e:
            logger.error(f"Keycloak setup failed: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Keycloak"""
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.authenticate_user(username, password)
        except Exception as e:
            logger.error(f"User authentication failed for {username}: {str(e)}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with Keycloak"""
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.verify_token(token)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from token"""
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.get_user_info(token)
        except Exception as e:
            logger.error(f"User info retrieval failed: {str(e)}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token"""
        try:
            _, _, auth_service, _ = self._get_services()
            return await auth_service.refresh_token(refresh_token)
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None
    
    async def ensure_admin_user_exists(self) -> bool:
        """Ensure admin user exists in both Keycloak and local database"""
        try:
            _, user_service, _, _ = self._get_services()
            
            admin_token = await user_service.setup_service.get_admin_token()
            if not admin_token:
                logger.error("Failed to get admin token")
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
                        logger.info("Admin user already exists in Keycloak")
                    else:
                        keycloak_exists = await user_service.create_admin_user()
                else:
                    logger.warning(f"Failed to search for admin user: {response.status}")
                    keycloak_exists = False
            
            local_exists = await user_service.create_local_admin_user()
            
            return keycloak_exists and local_exists
            
        except Exception as e:
            logger.error(f"Admin user check failed: {str(e)}")
            return False
    
    async def create_demo_users(self) -> bool:
        """Create demo users"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_demo_users()
        except Exception as e:
            logger.error(f"Demo user creation failed: {str(e)}")
            return False
    
    async def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str, role: str) -> Optional[str]:
        """Create a new user"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.create_user(username, email, first_name, last_name, password, role)
        except Exception as e:
            logger.error(f"User creation failed for {username}: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, username: str = None, email: str = None, first_name: str = None, last_name: str = None, role: str = None) -> bool:
        """Update user information"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.update_user(user_id, username, email, first_name, last_name, role)
        except Exception as e:
            logger.error(f"User update failed for {user_id}: {str(e)}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.delete_user(user_id)
        except Exception as e:
            logger.error(f"User deletion failed for {user_id}: {str(e)}")
            return False
    
    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Get user ID by username"""
        try:
            _, user_service, _, _ = self._get_services()
            return await user_service.get_user_id_by_username(username)
        except Exception as e:
            logger.error(f"Failed to get user ID for {username}: {str(e)}")
            return None
