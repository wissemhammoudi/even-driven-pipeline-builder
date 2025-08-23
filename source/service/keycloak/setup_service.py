import asyncio
import aiohttp
from typing import Dict, Optional
from source.config.config import keycloak_config

class KeycloakSetupService:
    def __init__(self, session: aiohttp.ClientSession):
        self.config = keycloak_config
        self.session = session
        
    async def get_admin_token(self) -> Optional[str]:
        try:
            token_url = f"{self.config.server_url}/realms/master/protocol/openid-connect/token"
            data = {
                "username": self.config.admin_username,
                "password": self.config.admin_password,
                "grant_type": "password",
                "client_id": "admin-cli"
            }
            
            async with self.session.post(token_url, data=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return token_data.get("access_token")
                else:
                    return None
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
    
    async def check_and_create_realm(self) -> bool:
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            realm_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}"
            async with self.session.get(realm_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return True
            
            realm_data = {
                "realm": self.config.realm_name,
                "enabled": True,
                "displayName": self.config.realm_display_name,
                "loginWithEmailAllowed": True,
                "duplicateEmailsAllowed": False
            }
            
            create_url = f"{self.config.server_url}/admin/realms"
            async with self.session.post(create_url, headers=headers, json=realm_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 201:
                    return True
                else:
                    return False
                    
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def create_client(self) -> bool:
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            client_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/clients"
            async with self.session.get(client_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    existing_clients = await response.json()
                    for client in existing_clients:
                        if client.get("clientId") == self.config.client_id:
                            return True
            
            client_data = {
                "clientId": self.config.client_id,
                "enabled": True,
                "publicClient": False,
                "secret": self.config.client_secret,
                "redirectUris": self.config.redirect_uris,
                "webOrigins": self.config.web_origins,
                "standardFlowEnabled": True,
                "directAccessGrantsEnabled": True,
                "serviceAccountsEnabled": True,
                "authorizationServicesEnabled": True,
                "protocol": "openid-connect"
            }
            
            async with self.session.post(client_url, headers=headers, json=client_data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 201:
                    client_id = None
                    async with self.session.get(client_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as get_response:
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
                    return False
                    
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def create_roles(self) -> bool:
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
                async with self.session.post(role_url, headers=headers, json=role, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 201:
                        pass
            
            return True
            
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def _configure_client_roles(self, client_id: str, admin_token: str) -> bool:
        try:
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            scope_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/client-scopes"
            async with self.session.get(scope_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as get_scope_response:
                if get_scope_response.status == 200:
                    scopes = await get_scope_response.json()
                    roles_scope_id = None
                    for scope in scopes:
                        if scope.get("name") == "roles":
                            roles_scope_id = scope.get("id")
                            break
                    
                    if roles_scope_id:
                        client_scope_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/clients/{client_id}/default-client-scopes/{roles_scope_id}"
                        async with self.session.put(client_scope_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as scope_response:
                            if scope_response.status == 204:
                                return True
                            else:
                                return False
                    else:
                        return False
                else:
                    return False
            
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            return False
    
    async def _get_role_id(self, role_name: str) -> Optional[str]:
        try:
            admin_token = await self.get_admin_token()
            if not admin_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            role_url = f"{self.config.server_url}/admin/realms/{self.config.realm_name}/roles/{role_name}"
            async with self.session.get(role_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    role_data = await response.json()
                    return role_data.get("id")
                return None
                
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
