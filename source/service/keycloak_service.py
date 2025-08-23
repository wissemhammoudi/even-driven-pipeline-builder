import asyncio
import aiohttp
import json
import logging
from typing import Dict, Optional, List
from source.config.config import keycloak_config, application_user_init_config

logger = logging.getLogger(__name__)

class KeycloakService:
    def __init__(self):
        self.config = keycloak_config
        self.admin_token = None
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_connection(self) -> Dict[str, bool]:
        """Test if Keycloak is reachable"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.config.server_url}/realms/master") as response:
                return {"reachable": response.status == 200}
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {"reachable": False}
    
    async def wait_for_ready(self, max_attempts: int = 15, delay: float = 3.0) -> bool:
        """Wait for Keycloak to be ready"""
        for attempt in range(max_attempts):
            try:
                result = await self.test_connection()
                if result["reachable"]:
                    logger.info("Keycloak is ready")
                    return True
                logger.info(f"Keycloak not ready, attempt {attempt + 1}/{max_attempts}")
                await asyncio.sleep(delay)
            except Exception as e:
                logger.error(f"Error checking Keycloak readiness: {e}")
                await asyncio.sleep(delay)
        return False
    
    async def get_admin_token(self) -> Optional[str]:
        """Get admin token for Keycloak operations"""
        try:
            token_url = f"{self.config.server_url}/realms/master/protocol/openid-connect/token"
            data = {
                "username": self.config.admin_username,
                "password": self.config.admin_password,
                "grant_type": "password",
                "client_id": "admin-cli"
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return token_data.get("access_token")
                else:
                    logger.error(f"Failed to get admin token: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting admin token: {e}")
            return None
    
    async def check_and_create_realm(self) -> bool:
        """Check if realm exists, create if it doesn't"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            realm_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}"
            async with self.session.get(realm_url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Realm {self.config.realm_name} already exists")
                    return True
            
            realm_data = {
                "realm": self.config.realm_name,
                "enabled": True,
                "displayName": "Pipeline Realm",
                "loginWithEmailAllowed": True,
                "duplicateEmailsAllowed": False
            }
            
            create_url = f"{self.config.server_url}/admin/realms"
            async with self.session.post(create_url, headers=headers, json=realm_data) as response:
                if response.status == 201:
                    logger.info(f"Realm {self.config.realm_name} created successfully")
                    return True
                else:
                    logger.error(f"Failed to create realm: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking/creating realm: {e}")
            return False
    
    async def create_client(self) -> bool:
        """Create the client application in Keycloak"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            client_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/clients"
            async with self.session.get(client_url, headers=headers) as response:
                if response.status == 200:
                    existing_clients = await response.json()
                    for client in existing_clients:
                        if client.get("clientId") == self.config.client_id:
                            logger.info(f"Client {self.config.client_id} already exists")
                            return True
            
            client_data = {
                "clientId": self.config.client_id,
                "enabled": True,
                "publicClient": False,
                "secret": self.config.client_secret,
                "redirectUris": ["http://localhost:3000/*", "http://localhost:3001/*"],
                "webOrigins": ["http://localhost:3000", "http://localhost:3001"],
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,
                "serviceAccountsEnabled": True,
                "authorizationServicesEnabled": True,
                "protocol": "openid-connect"
            }
            
            async with self.session.post(client_url, headers=headers, json=client_data) as response:
                if response.status == 201:
                    logger.info(f"Client {self.config.client_id} created successfully")
                    
                    client_id = None
                    async with self.session.get(client_url, headers=headers) as get_response:
                        if get_response.status == 200:
                            clients = await get_response.json()
                            for client in clients:
                                if client.get("clientId") == self.config.client_id:
                                    client_id = client.get("id")
                                    break
                    
                    if client_id:
                        await self._configure_client_roles(client_id, admin_token)
                    
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create client: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            return False
    
    async def create_roles(self) -> bool:
        """Create default roles in the realm"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            roles = [
                {"name": "admin", "description": "Administrator role"},
                {"name": "user", "description": "Regular user role"},
                {"name": "viewer", "description": "Read-only user role"}
            ]
            
            for role in roles:
                role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/roles"
                async with self.session.post(role_url, headers=headers, json=role) as response:
                    if response.status != 201:
                        logger.warning(f"Failed to create role {role['name']}: {response.status}")
            
            logger.info("Default roles created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating roles: {e}")
            return False
    
    async def create_admin_user(self) -> bool:
        """Create the initial admin user"""
        try:
            admin_token = await self.get_admin_token()
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
                        logger.info("Admin user already exists in Keycloak")
                        return True
            
            user_data = {
                "username": application_user_init_config.admin_username,
                "email": application_user_init_config.admin_email,
                "firstName": application_user_init_config.admin_first_name,
                "lastName": application_user_init_config.admin_last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": application_user_init_config.admin_password,
                    "temporary": False
                }]
            }
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
            async with self.session.post(user_url, headers=headers, json=user_data) as response:
                if response.status == 201:
                    user_id = response.headers.get("Location", "").split("/")[-1]
                    
                    role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                    admin_role = await self._get_role_id("admin")
                    if admin_role:
                        role_data = [{"id": admin_role, "name": "admin"}]
                        async with self.session.post(role_url, headers=headers, json=role_data) as role_response:
                            if role_response.status == 204:
                                logger.info("Admin user created and role assigned successfully")
                                return True
                    
                    logger.info("Admin user created successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create admin user: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            return False
    
    async def create_local_admin_user(self) -> bool:
        """Create the admin user in the local database"""
        try:
            from source.models.user.models import User
            from source.schema.user.schemas import UserRole
            from source.repository.user.repository import UserRepository
            
            user_repository = UserRepository()
            
            try:
                existing_user = user_repository.get_user_by_username(
                    application_user_init_config.admin_username
                )
                if existing_user:
                    logger.info("Admin user already exists in local database")
                    return True
            except:
                pass
            
            # Get the existing admin user from Keycloak to get the user ID
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to find admin user")
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Search for the admin user in Keycloak
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={application_user_init_config.admin_username}"
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        keycloak_user_id = users[0].get("id")
                        logger.info(f"Found admin user in Keycloak with ID: {keycloak_user_id}")
                        
                        # Create user directly in local database
                        user = User(
                            user_id=keycloak_user_id,
                            username=application_user_init_config.admin_username,
                            email=application_user_init_config.admin_email,
                            first_name=application_user_init_config.admin_first_name,
                            last_name=application_user_init_config.admin_last_name,
                            role=UserRole.admin
                        )
                        
                        user_repository.create_user(user)
                        logger.info("Admin user created in local database")
                        return True
                    else:
                        logger.error("Admin user not found in Keycloak")
                        return False
                else:
                    logger.error(f"Failed to search for admin user in Keycloak: {response.status}")
                    return False
            
        except Exception as e:
            logger.error(f"Error creating local admin user: {e}")
            return False
    
    async def _configure_client_roles(self, client_id: str, admin_token: str) -> bool:
        """Configure client to include roles in tokens"""
        try:
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # First, try to get the roles client scope ID
            scope_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/client-scopes"
            async with self.session.get(scope_url, headers=headers) as get_scope_response:
                if get_scope_response.status == 200:
                    scopes = await get_scope_response.json()
                    roles_scope_id = None
                    for scope in scopes:
                        if scope.get("name") == "roles":
                            roles_scope_id = scope.get("id")
                            break
                    
                    if roles_scope_id:
                        # Add the roles scope to the client
                        client_scope_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/clients/{client_id}/default-client-scopes/{roles_scope_id}"
                        async with self.session.put(client_scope_url, headers=headers) as scope_response:
                            if scope_response.status == 204:
                                logger.info(f"Added roles scope to client {self.config.client_id}")
                                return True
                            else:
                                logger.warning(f"Failed to add roles scope to client: {scope_response.status}")
                                return False
                    else:
                        logger.warning("Roles client scope not found")
                        return False
                else:
                    logger.warning(f"Failed to get client scopes: {get_scope_response.status}")
                    return False
            
        except Exception as e:
            logger.error(f"Error configuring client roles: {e}")
            return False

    async def _get_role_id(self, role_name: str) -> Optional[str]:
        """Get role ID by name"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/roles/{role_name}"
            async with self.session.get(role_url, headers=headers) as response:
                if response.status == 200:
                    role_data = await response.json()
                    return role_data.get("id")
                return None
                
        except Exception as e:
            logger.error(f"Error getting role ID: {e}")
            return None
    
    async def setup_keycloak(self) -> Dict[str, any]:
        """Complete Keycloak setup"""
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
            logger.error(f"Keycloak setup failed: {e}")
            return {"success": False, "message": str(e)}
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with Keycloak"""
        try:
            token_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token"
            data = {
                "username": username,
                "password": password,
                "grant_type": "password",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type")
                    }
                else:
                    logger.warning(f"Authentication failed for user {username}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            introspect_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/token/introspect"
            data = {
                "token": token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with self.session.post(introspect_url, data=data) as response:
                if response.status == 200:
                    token_info = await response.json()
                    if token_info.get("active", False):
                        logger.info(f"Token info: {token_info}")
                        logger.info(f"Realm access: {token_info.get('realm_access', {})}")
                        logger.info(f"Roles: {token_info.get('realm_access', {}).get('roles', [])}")
                        
                        return {
                            "user_id": token_info.get("sub"),
                            "username": token_info.get("preferred_username"),
                            "email": token_info.get("email"),
                            "roles": token_info.get("realm_access", {}).get("roles", []),
                            "exp": token_info.get("exp")
                        }
                return None
                
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict]:
        """Get user information from token"""
        try:
            userinfo_url = f"{self.config.server_url}/realms/{self.config.realm_name}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(userinfo_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    async def ensure_admin_user_exists(self) -> bool:
        """Ensure admin user exists in both Keycloak and local database"""
        try:
            logger.info("Ensuring admin user exists...")
            
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to check user existence")
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
                        logger.info("Admin user already exists in Keycloak")
                        keycloak_exists = True
                    else:
                        logger.info("Admin user does not exist in Keycloak, creating...")
                        keycloak_exists = await self.create_admin_user()
                else:
                    logger.error(f"Failed to search for admin user: {response.status}")
                    keycloak_exists = False
            
            local_exists = await self.create_local_admin_user()
            
            return keycloak_exists and local_exists
            
        except Exception as e:
            logger.error(f"Error ensuring admin user exists: {e}")
            return False
    
    async def create_demo_users(self) -> bool:
        """Create demo users for testing purposes"""
        try:
            logger.info("Creating demo users...")
            
            demo_users = [
                {
                    "username": "user",
                    "email": "user@example.com",
                    "first_name": "Regular",
                    "last_name": "User",
                    "password": "user123",
                    "role": "user"
                }
            ]
            
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to create demo users")
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            created_count = 0
            for user_data in demo_users:
                try:
                    keycloak_user_data = {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "firstName": user_data["first_name"],
                        "lastName": user_data["last_name"],
                        "enabled": True,
                        "emailVerified": True,
                        "credentials": [{
                            "type": "password",
                            "value": user_data["password"],
                            "temporary": False
                        }]
                    }
                    
                    user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
                    async with self.session.post(user_url, headers=headers, json=keycloak_user_data) as response:
                        if response.status == 201:
                            user_id = response.headers.get("Location", "").split("/")[-1]
                            
                            role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                            role = await self._get_role_id(user_data["role"])
                            if role:
                                role_data = [{"id": role, "name": user_data["role"]}]
                                async with self.session.post(role_url, headers=headers, json=role_data) as role_response:
                                    if role_response.status == 204:
                                        logger.info(f"Demo user {user_data['username']} created and role assigned successfully")
                                        created_count += 1
                                    else:
                                        logger.warning(f"Demo user {user_data['username']} created but role assignment failed")
                                        created_count += 1
                            else:
                                logger.warning(f"Demo user {user_data['username']} created but role not found")
                                created_count += 1
                        else:
                            logger.warning(f"Failed to create demo user {user_data['username']}: {response.status}")
                            
                except Exception as e:
                    logger.error(f"Error creating demo user {user_data['username']}: {e}")
            
            logger.info(f"Created {created_count} demo users")
            return created_count > 0
            
        except Exception as e:
            logger.error(f"Error creating demo users: {e}")
            return False

    async def create_user(self, username: str, email: str, first_name: str, last_name: str, password: str, role: str) -> str:
        """Create a new user in Keycloak"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to create user")
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            keycloak_user_data = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False
                }]
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={username}"
            async with self.session.get(search_url, headers=headers) as search_response:
                if search_response.status == 200:
                    existing_users = await search_response.json()
                    if existing_users:
                        logger.info(f"User {username} already exists in Keycloak")
                        
                        return existing_users[0].get("id")
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users"
            async with self.session.post(user_url, headers=headers, json=keycloak_user_data) as response:
                if response.status == 201:
                    user_id = response.headers.get("Location", "").split("/")[-1]
                    
                    role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}/role-mappings/realm"
                    role_id = await self._get_role_id(role)
                    if role_id:
                        role_data = [{"id": role_id, "name": role}]
                        async with self.session.post(role_url, headers=headers, json=role_data) as role_response:
                            if role_response.status == 204:
                                logger.info(f"User {username} created and role assigned successfully")
                                return user_id
                            else:
                                logger.warning(f"User {username} created but role assignment failed")
                                return user_id  # User created, role assignment failed
                    else:
                        logger.warning(f"User {username} created but role not found")
                        return user_id  # User created, role not found
                else:
                    logger.error(f"Failed to create user {username}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None

    async def update_user(self, user_id: str, username: str = None, email: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Update an existing user in Keycloak"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to update user")
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            update_data = {}
            if username is not None:
                update_data["username"] = username
            if email is not None:
                update_data["email"] = email
            if first_name is not None:
                update_data["firstName"] = first_name
            if last_name is not None:
                update_data["lastName"] = last_name
            
            if not update_data:
                return True  
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}"
            async with self.session.put(user_url, headers=headers, json=update_data) as response:
                if response.status == 204:
                    logger.info(f"User {user_id} updated successfully")
                    return True
                else:
                    logger.error(f"Failed to update user {user_id}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user from Keycloak"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to delete user")
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            user_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users/{user_id}"
            async with self.session.delete(user_url, headers=headers) as response:
                if response.status == 204:
                    logger.info(f"User {user_id} deleted successfully")
                    return True
                else:
                    logger.error(f"Failed to delete user {user_id}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Get Keycloak user ID by username"""
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                logger.error("Cannot get admin token to search for user")
                return None
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            search_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/users?username={username}"
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    users = await response.json()
                    if users:
                        return users[0].get("id")
                    else:
                        return None
                else:
                    logger.error(f"Failed to search for user {username}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching for user {username}: {e}")
            return None


keycloak_service = None

def get_keycloak_service():
    """Get or create KeycloakService instance"""
    global keycloak_service
    if keycloak_service is None:
        keycloak_service = KeycloakService()
    return keycloak_service
