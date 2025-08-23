import logging
from typing import Optional
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
            
            # Determine Superset roles based on user role
            if role == UserRole.admin:
                superset_roles = [superset_config.superset_admin_role_id]
                logger.debug(f"Assigning admin role to user {username}")
            else:
                superset_roles = [superset_config.superset_gamma_role_id]
                logger.debug(f"Assigning gamma role to user {username}")
            
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
                return None
                
        except Exception as e:
            logger.error(f"Failed to create user {username} in Superset: {str(e)}")
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
