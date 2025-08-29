import logging
from typing import Optional, Dict
from source.schema.user.schemas import UserRole
from source.config.config import superset_config
from source.service.PipelineManager.supersetclient import SupersetClient
from source.service.user_superset_account_association.service import UserSupersetAccountAssociationService

# Configure logging
logger = logging.getLogger(__name__)

class UserSupersetService:
    def __init__(self):
        self.superset_client = SupersetClient(
            base_url=superset_config.superset_url,
            username=superset_config.superset_user,
            password=superset_config.superset_password
        )
        self.user_superset_account_association_service = UserSupersetAccountAssociationService()
    
    def _get_superset_roles(self) -> Dict[str, int]:
        """
        Get actual role IDs from Superset
        
        Returns:
            Dictionary mapping role names to role IDs
        """
        try:
            if not self.superset_client.authenticate():
                logger.error("Failed to authenticate with Superset to get roles")
                return {}
            
            # Get all roles from Superset
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
                            logger.debug(f"Found role: {role_name} (ID: {role_id})")
                
                logger.info(f"Retrieved {len(roles)} roles from Superset")
                return roles
            else:
                logger.warning(f"Failed to get roles from Superset (status: {response.status_code})")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting Superset roles: {str(e)}")
            return {}

    def create_user(self, username: str, email: str, first_name: str, last_name: str, role: UserRole) -> Optional[int]:
        """
        Create user in Superset and return the user ID
        
        Args:
            username: User's username
            email: User's email
            first_name: User's first name
            last_name: User's last name
            role: User's role
            
        Returns:
            Superset user ID if successful, None otherwise
        """
        try:
            if not username or not email:
                logger.error("Username and email are required for Superset user creation")
                return None
                
            logger.info(f"Creating user {username} in Superset")
            
            # Ensure we're authenticated with Superset
            if not self.superset_client.authenticate():
                logger.error(f"Failed to authenticate with Superset for user creation: {username}")
                logger.error(f"Superset URL: {self.superset_client.base_url}")
                logger.error(f"Admin credentials: {self.superset_client.username}")
                return None
            
            logger.info(f"Successfully authenticated with Superset as {self.superset_client.username}")
            
            # Get actual role IDs from Superset
            superset_roles = self._get_superset_roles()
            
            # Determine Superset roles based on user role
            if role == UserRole.admin:
                # Try configured admin role ID first, then fallback to actual roles
                if superset_roles.get('admin'):
                    role_id = superset_roles['admin']
                    logger.debug(f"Using actual admin role ID: {role_id}")
                else:
                    role_id = superset_config.superset_admin_role_id
                    logger.debug(f"Using configured admin role ID: {role_id}")
                superset_roles = [role_id]
                logger.debug(f"Assigning admin role (ID: {role_id}) to user {username}")
            else:
                # Try configured gamma role ID first, then fallback to actual roles
                if superset_roles.get('gamma'):
                    role_id = superset_roles['gamma']
                    logger.debug(f"Using actual gamma role ID: {role_id}")
                else:
                    role_id = superset_config.superset_gamma_role_id
                    logger.debug(f"Using configured gamma role ID: {role_id}")
                superset_roles = [role_id]
                logger.debug(f"Assigning gamma role (ID: {role_id}) to user {username}")
            
            # Check if the role exists in Superset before creating user
            try:
                # Try to get role info to verify it exists
                role_check_url = f"{self.superset_client.base_url}/api/v1/security/roles/{superset_roles[0]}"
                role_response = self.superset_client.session.get(
                    role_check_url,
                    headers={'Authorization': f'Bearer {self.superset_client.access_token}'}
                )
                if role_response.status_code != 200:
                    logger.warning(f"Role ID {superset_roles[0]} may not exist in Superset (status: {role_response.status_code})")
                    logger.warning(f"Response: {role_response.text}")
            except Exception as e:
                logger.warning(f"Could not verify role existence: {str(e)}")
            
            logger.info(f"Attempting to create user {username} with roles: {superset_roles}")
            
            superset_user_id = self.superset_client.create_user(
                username=username,
                email=email,
                first_name=first_name or "",
                last_name=last_name or "",
                password=username,  # Using username as initial password
                roles=superset_roles,
                active=True
            )
            
            if superset_user_id:
                logger.info(f"User {username} created successfully in Superset with ID: {superset_user_id}")
                return superset_user_id
            else:
                logger.error(f"Failed to create user {username} in Superset - no user ID returned")
                # Try to get more details about the failure
                try:
                    # Check if user already exists
                    existing_user = self.superset_client.get_user_id(username)
                    if existing_user:
                        logger.info(f"User {username} already exists in Superset with ID: {existing_user}")
                        return existing_user
                except Exception as e:
                    logger.debug(f"Could not check for existing user: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create user {username} in Superset: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return None
    
    def create_admin_user(self, username: str, email: str) -> Optional[int]:
        """
        Create admin user in Superset
        
        Args:
            username: Admin username
            email: Admin email
            
        Returns:
            Superset user ID if successful, None otherwise
        """
        try:
            logger.info(f"Creating admin user {username} in Superset")
            return self.create_user(
                username=username,
                email=email,
                first_name="Admin",
                last_name="User",
                role=UserRole.admin
            )
        except Exception as e:
            logger.error(f"Failed to create admin user {username} in Superset: {str(e)}")
            return None
    
    def create_regular_user(self, username: str, email: str) -> Optional[int]:
        """
        Create regular user in Superset
        
        Args:
            username: Regular user username
            email: Regular user email
            
        Returns:
            Superset user ID if successful, None otherwise
        """
        try:
            logger.info(f"Creating regular user {username} in Superset")
            return self.create_user(
                username=username,
                email=email,
                first_name="Regular",
                last_name="User",
                role=UserRole.user
            )
        except Exception as e:
            logger.error(f"Failed to create regular user {username} in Superset: {str(e)}")
            return None
    
    def add_user_association(self, user_id: str, superset_user_id: int) -> bool:
        """
        Add association between local user and Superset user
        
        Args:
            user_id: Local user ID
            superset_user_id: Superset user ID
            
        Returns:
            True if association successful, False otherwise
        """
        try:
            if not user_id or not superset_user_id:
                logger.error("Both user_id and superset_user_id are required for association")
                return False
                
            logger.info(f"Adding association between local user {user_id} and Superset user {superset_user_id}")
            
            self.user_superset_account_association_service.add_association(
                user_id=user_id, 
                superset_user_id=superset_user_id
            )
            
            logger.info(f"Association added successfully between local user {user_id} and Superset user {superset_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add association between local user {user_id} and Superset user {superset_user_id}: {str(e)}")
            return False
