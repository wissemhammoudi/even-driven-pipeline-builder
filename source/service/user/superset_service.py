from typing import Optional, Dict
from source.schema.user.schemas import UserRole
from source.config.config import superset_config
from source.service.PipelineManager.supersetclient import SupersetClient
from source.service.user_superset_account_association.service import UserSupersetAccountAssociationService


class UserSupersetService:
    def __init__(self):
        self.superset_client = SupersetClient(
            base_url=superset_config.superset_url,
            username=superset_config.superset_user,
            password=superset_config.superset_password
        )
        self.user_superset_account_association_service = UserSupersetAccountAssociationService()
    
    def _get_superset_roles(self) -> Dict[str, int]:

        try:
            if not self.superset_client.authenticate():
                raise Exception("Failed to authenticate with Superset to get roles")
            
            roles_url = f"{self.superset_client.base_url}/api/v1/security/roles/"
            response = self.superset_client.session.get(
                roles_url,
                headers={'Authorization': f'Bearer {self.superset_client.access_token}'}
            )
            
            if response.status_code == 200:
                roles_data = response.json()
                roles = {}
                
                if 'result' in roles_data:
                    for role in roles_data['result']:
                        role_name = role.get('name', '').lower()
                        role_id = role.get('id')
                        if role_id is not None:
                            roles[role_name] = role_id
                return roles
            else:
                return {}
                
        except Exception as e:
            raise Exception(f"Error getting Superset roles: {str(e)}")

    def create_user(self, username: str, email: str, first_name: str, last_name: str, role: UserRole) -> Optional[int]:

        try:
            if not username or not email:
                raise Exception("Username and email are required for Superset user creation")
                
            if not self.superset_client.authenticate():
                raise Exception(f"Failed to authenticate with Superset for user creation: {username}")
            
            superset_roles = self._get_superset_roles()
            
            if role == UserRole.admin:
                if superset_roles.get('admin'):
                    role_id = superset_roles['admin']
                else:
                    role_id = superset_config.superset_admin_role_id
                superset_roles = [role_id]
            else:
                if superset_roles.get('gamma'):
                    role_id = superset_roles['gamma']
                else:
                    role_id = superset_config.superset_gamma_role_id
                superset_roles = [role_id]
            
            try:
                role_check_url = f"{self.superset_client.base_url}/api/v1/security/roles/{superset_roles[0]}"
                role_response = self.superset_client.session.get(
                    role_check_url,
                    headers={'Authorization': f'Bearer {self.superset_client.access_token}'}
                )
                if role_response.status_code != 200:
                    raise Exception(f"Role ID {superset_roles[0]} may not exist in Superset (status: {role_response.status_code})")
            except Exception as e:
                raise Exception(f"Could not verify role existence: {str(e)}")
            
            superset_user_id = self.superset_client.create_user(
                username=username,
                email=email,
                first_name=first_name or "",
                last_name=last_name or "",
                password=username,
                roles=superset_roles,
                active=True
            )
            
            if superset_user_id:
                return superset_user_id
            else:
                try:
                    existing_user = self.superset_client.get_user_id(username)
                    if existing_user:
                        return existing_user
                except Exception as e:
                    raise Exception(f"Could not check for existing user: {str(e)}")
                return None
                
        except Exception as e:
            return None
    
    def create_admin_user(self, username: str, email: str) -> Optional[int]:

        try:
            return self.create_user(
                username=username,
                email=email,
                first_name="Admin",
                last_name="User",
                role=UserRole.admin
            )
        except Exception as e:
            raise Exception(f"Failed to create admin user {username} in Superset: {str(e)}")
    
    def create_regular_user(self, username: str, email: str) -> Optional[int]:

        try:
            return self.create_user(
                username=username,
                email=email,
                first_name="Regular",
                last_name="User",
                role=UserRole.user
            )
        except Exception as e:
            raise Exception(f"Failed to create regular user {username} in Superset: {str(e)}")
    
    def add_user_association(self, user_id: str, superset_user_id: int) -> bool:

        try:
            if not user_id or not superset_user_id:
                raise Exception("Both user_id and superset_user_id are required for association")
                
            self.user_superset_account_association_service.add_association(
                user_id=user_id, 
                superset_user_id=superset_user_id
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to add association between local user {user_id} and Superset user {superset_user_id}: {str(e)}")
