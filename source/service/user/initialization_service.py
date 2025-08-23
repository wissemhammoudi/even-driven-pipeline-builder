import logging
from typing import List
from source.schema.user.schemas import UserCreate, UserRole
from source.config.config import application_user_init_config
from source.models.user.models import User
from source.repository.user.repository import UserRepository
from .keycloak_service import UserKeycloakService
from .superset_service import UserSupersetService

# Configure logging
logger = logging.getLogger(__name__)

class UserInitializationService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.keycloak_service = UserKeycloakService()
        self.superset_service = UserSupersetService()
    
    async def create_initial_users(self) -> List[str]:
        """
        Create admin and regular user if they don't exist
        
        Returns:
            List of usernames created
            
        Raises:
            Exception: If initialization fails
        """
        users_created = []
        
        try:
            logger.info("Starting initial user creation process")
            
            # Create admin user
            admin_created = await self._create_admin_user()
            if admin_created:
                users_created.append(application_user_init_config.admin_username)
            
            # Create regular user
            regular_created = await self._create_regular_user()
            if regular_created:
                users_created.append(application_user_init_config.user_username)
            
            if users_created:
                logger.info(f"Successfully created initial users: {', '.join(users_created)}")
            else:
                logger.info("No new initial users were created")
                
            return users_created
            
        except Exception as e:
            logger.error(f"Failed to create initial users: {str(e)}")
            raise
    
    async def _create_admin_user(self) -> bool:
        """
        Create admin user if it doesn't exist
        
        Returns:
            True if user was created, False if already exists
        """
        try:
            admin_username = application_user_init_config.admin_username
            logger.info(f"Checking if admin user {admin_username} exists")
            
            # Check if admin user already exists
            existing_admin = self.user_repository.get_user_by_username(admin_username)
            if existing_admin:
                logger.info(f"Admin user {admin_username} already exists")
                return False
            
            logger.info(f"Creating admin user {admin_username}")
            
            # Create user in Keycloak
            admin_keycloak_id = await self.keycloak_service.create_user(UserCreate(
                username=admin_username,
                email=application_user_init_config.admin_email,
                first_name=application_user_init_config.admin_first_name,
                last_name=application_user_init_config.admin_last_name,
                password=application_user_init_config.admin_password,
                role=UserRole.admin
            ))
            
            if not admin_keycloak_id:
                logger.error(f"Failed to create admin user {admin_username} in Keycloak")
                return False
            
            # Create user in local database
            admin_user = User(
                user_id=admin_keycloak_id,  
                username=admin_username,
                email=application_user_init_config.admin_email,
                first_name=application_user_init_config.admin_first_name,
                last_name=application_user_init_config.admin_last_name,
                role=UserRole.admin
            )
            self.user_repository.create_user(admin_user)
            logger.info(f"Admin user {admin_username} created in local database")
            
            # Create user in Superset
            try:
                superset_user_id = self.superset_service.create_admin_user(
                    username=admin_username,
                    email=application_user_init_config.admin_email
                )
                
                if superset_user_id:
                    self.superset_service.add_user_association(
                        user_id=admin_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    logger.info(f"Admin user {admin_username} created in Superset with ID: {superset_user_id}")
                else:
                    logger.warning(f"Failed to create admin user {admin_username} in Superset")
                    
            except Exception as e:
                logger.error(f"Failed to create admin user {admin_username} in Superset: {str(e)}")
            
            logger.info(f"Admin user {admin_username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create admin user {admin_username}: {str(e)}")
            return False
    
    async def _create_regular_user(self) -> bool:
        """
        Create regular user if it doesn't exist
        
        Returns:
            True if user was created, False if already exists
        """
        try:
            regular_username = application_user_init_config.user_username
            logger.info(f"Checking if regular user {regular_username} exists")
            
            # Check if regular user already exists
            existing_regular = self.user_repository.get_user_by_username(regular_username)
            if existing_regular:
                logger.info(f"Regular user {regular_username} already exists")
                return False
            
            logger.info(f"Creating regular user {regular_username}")
            
            # Create user in Keycloak
            regular_keycloak_id = await self.keycloak_service.create_user(UserCreate(
                username=regular_username,
                email=application_user_init_config.user_email,
                first_name=application_user_init_config.user_first_name,
                last_name=application_user_init_config.user_last_name,
                password=application_user_init_config.user_password,
                role=UserRole.user
            ))
            
            if not regular_keycloak_id:
                logger.error(f"Failed to create regular user {regular_username} in Keycloak")
                return False
            
            # Create user in local database
            regular_user = User(
                user_id=regular_keycloak_id,  
                username=regular_username,
                email=application_user_init_config.user_email,
                first_name=application_user_init_config.user_first_name,
                last_name=application_user_init_config.user_last_name,
                role=UserRole.user
            )
            self.user_repository.create_user(regular_user)
            logger.info(f"Regular user {regular_username} created in local database")
            
            # Create user in Superset
            try:
                superset_user_id = self.superset_service.create_regular_user(
                    username=regular_username,
                    email=application_user_init_config.user_email
                )
                
                if superset_user_id:
                    self.superset_service.add_user_association(
                        user_id=regular_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    logger.info(f"Regular user {regular_username} created in Superset with ID: {superset_user_id}")
                else:
                    logger.warning(f"Failed to create regular user {regular_username} in Superset")
                    
            except Exception as e:
                logger.error(f"Failed to create regular user {regular_username} in Superset: {str(e)}")
            
            logger.info(f"Regular user {regular_username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create regular user {regular_username}: {str(e)}")
            return False
