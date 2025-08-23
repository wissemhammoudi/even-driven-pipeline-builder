from source.repository.user.repository import UserRepository
from source.schema.user.schemas import UserCreate, UserUpdate, UserResponse, PasswordUpdate, LoginSchema, UserRole
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.config.config import superset_config, application_user_init_config
from source.service.PipelineManager.supersetclient import SupersetClient
from source.service.user_superset_account_association.service import UserSupersetAccountAssociationService
from source.models.user.models import User
from source.service.authentication.keycloak_auth import keycloak_auth_service
from typing import List, Optional
from datetime import datetime
import hashlib

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.user_superset_account_association_service = UserSupersetAccountAssociationService()
        self.superset_client = SupersetClient(
            base_url=superset_config.superset_url,
            username=superset_config.superset_user,
            password=superset_config.superset_password
        )
    async def signup(self, user_data: UserCreate):
        """Create user in Keycloak first, then sync to local DB"""
        try:
            print(f"DEBUG: Starting user signup for {user_data.username}")
            print(f"DEBUG: User data: {user_data}")
            
            if self.user_repository.get_user_by_email_and_username(user_data.email, user_data.username):
                raise DuplicateUserError("Username or email already exists")
            
            print(f"DEBUG: Creating user in Keycloak...")
            keycloak_user_id = await self._create_keycloak_user(user_data)
            print(f"DEBUG: Keycloak user ID: {keycloak_user_id}")
            if not keycloak_user_id:
                raise Exception("Failed to create user in Keycloak")
            
            print(f"DEBUG: Creating user in local database...")
            user = User(
                user_id=keycloak_user_id,  
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role or UserRole.user
            )
            print(f"DEBUG: User object created: {user}")
            created_user = self.user_repository.create_user(user)
            print(f"DEBUG: User created in database: {created_user}")
            
            if user_data.role == UserRole.admin:
                superset_roles = [superset_config.superset_admin_role_id]
            else:
                superset_roles = [superset_config.superset_gamma_role_id]
            
            superset_user_id = self.superset_client.create_user(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                password=user_data.username,
                roles=superset_roles,
                active=True
            )
            
            if superset_user_id:
                self.user_superset_account_association_service.add_association(
                    user_id=keycloak_user_id, 
                    superset_user_id=superset_user_id
                )
            
            return {
                "message": "User created successfully in Keycloak and local database",
                "user_id": keycloak_user_id
            }
            
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def get_all_users(self):
        return self.user_repository.get_all_active_user()
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0):
        """Get all users with filtering and pagination"""
        return self.user_repository.get_all_users_filtered(search=search, role=role, limit=limit, offset=offset)
    
    def get_user_by_id(self, user_id: str):
        return self.user_repository.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str):
        user = self.user_repository.get_active_user_by_username(username, )
        if not user:
            raise UserNotFoundError(f"User with username '{username}' not found")
        return user

    async def delete_user(self, user_id: str):
        """Delete user from Keycloak first, then sync to local DB"""
        try:
            user = self.user_repository.get_active_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            await self._delete_keycloak_user(user_id)
            
            self.user_repository.mark_deleted(user)
            return {"message": "User deleted successfully from Keycloak and local database"}
            
        except Exception as e:
            raise Exception(f"Failed to delete user: {str(e)}")

    def update_password(self, password_data: PasswordUpdate):
        user = self.user_repository.get_active_user_by_id(password_data.user_id, )
        if not user:
            raise UserNotFoundError(f"User with ID {password_data.user_id} not found")

        raise InvalidPasswordError("Password changes must be done through Keycloak")
        self.user_repository.commit()
        return {"message": "Password updated successfully"}

    async def update_user(self, user_data: UserUpdate):
        """Update user in Keycloak first, then sync to local DB"""
        try:
            user = self.user_repository.get_user_by_id(user_data.user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_data.user_id} not found")
            
            if user_data.email:
                existing_email = self.user_repository.get_user_by_email(user_data.email)
                if existing_email and existing_email.user_id != user.user_id:
                    raise DuplicateUserError("Email already exists")
            
            if user_data.username:
                existing_username = self.user_repository.get_user_by_username(user_data.username)
                if existing_username and existing_username.user_id != user.user_id:
                    raise DuplicateUserError("Username already exists")
            
            await self._update_keycloak_user(user_data)
            
            if user_data.email:
                user.email = user_data.email
            if user_data.username:
                user.username = user_data.username
            if user_data.first_name:
                user.first_name = user_data.first_name
            if user_data.last_name:
                user.last_name = user_data.last_name
            
            self.user_repository.commit()
            return {"message": "User information updated successfully in Keycloak and local database"}
            
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")

    async def login(self, login_data: LoginSchema):
        """Login using Keycloak authentication"""
        try:
            auth_result = await keycloak_auth_service.authenticate_user(
                login_data.username, 
                login_data.password
            )
            
            if not auth_result:
                raise InvalidPasswordError("Invalid username or password")  
            user = self.user_repository.get_active_user_by_username(login_data.username)
            if not user:
                raise UserNotFoundError(f"User with username '{login_data.username}' not found")
            
            return {
                "access_token": auth_result["access_token"],
                "refresh_token": auth_result["refresh_token"],
                "token_type": auth_result["token_type"],
                "expires_in": auth_result["expires_in"]
            }
        except Exception as e:
            raise InvalidPasswordError(f"Authentication failed: {str(e)}")

    async def create_initial_users(self):
        """Create admin and regular user if they don't exist"""
        users_created = []
        
        try:
            admin_user = self.user_repository.get_user_by_username(application_user_init_config.admin_username)
            if not admin_user:
                admin_keycloak_id = await self._create_keycloak_user(UserCreate(
                    username=application_user_init_config.admin_username,
                    email=application_user_init_config.admin_email,
                    first_name=application_user_init_config.admin_username,
                    last_name=application_user_init_config.admin_username,
                    password=application_user_init_config.admin_password,
                    role=UserRole.admin
                ))
                
                if not admin_keycloak_id:
                    print(f"Warning: Could not create admin user in Keycloak '{application_user_init_config.admin_username}'")
                    return users_created
                
                admin_user = User(
                    user_id=admin_keycloak_id,  
                    username=application_user_init_config.admin_username,
                    email=application_user_init_config.admin_email,
                    first_name=application_user_init_config.admin_username,
                    last_name=application_user_init_config.admin_username,
                    role=UserRole.admin
                )
                self.user_repository.create_user(admin_user)
                
                superset_roles = [superset_config.superset_admin_role_id]
                superset_user_id = self.superset_client.create_user(
                    username=application_user_init_config.admin_username,
                    email=application_user_init_config.admin_email,
                    first_name="Admin",
                    last_name="User",
                    password=application_user_init_config.admin_username,  
                    roles=superset_roles,
                    active=True
                )
                
                if superset_user_id:
                    self.user_superset_account_association_service.add_association(
                        user_id=admin_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    print(f"Superset account created for admin user '{application_user_init_config.admin_username}'")
                else:
                    print(f"Warning: Failed to create Superset account for admin user '{application_user_init_config.admin_username}'")
                
                users_created.append(application_user_init_config.admin_username)
                print(f"Admin user '{application_user_init_config.admin_username}' created")
            else:
                print(f"Admin user '{application_user_init_config.admin_username}' already exists, skipping...")
            
            regular_user = self.user_repository.get_user_by_username(application_user_init_config.user_username)
            if not regular_user:
                regular_keycloak_id = await self._create_keycloak_user(UserCreate(
                    username=application_user_init_config.user_username,
                    email=application_user_init_config.user_email,
                    first_name=application_user_init_config.user_username,
                    last_name=application_user_init_config.user_username,
                    password=application_user_init_config.user_password,
                    role=UserRole.user
                ))
                
                if not regular_keycloak_id:
                    print(f"Warning: Could not create regular user in Keycloak '{application_user_init_config.user_username}'")
                    return users_created
                
                regular_user = User(
                    user_id=regular_keycloak_id,  
                    username=application_user_init_config.user_username,
                    email=application_user_init_config.user_email,
                    first_name=application_user_init_config.user_username,
                    last_name=application_user_init_config.user_username,
                    role=UserRole.user
                )
                self.user_repository.create_user(regular_user)
                
                superset_roles = [superset_config.superset_gamma_role_id]
                superset_user_id = self.superset_client.create_user(
                    username=application_user_init_config.user_username,
                    email=application_user_init_config.user_email,
                    first_name="Regular",
                    last_name="User",
                    password=application_user_init_config.user_username,  
                    roles=superset_roles,
                    active=True
                )
                
                if superset_user_id:
                    self.user_superset_account_association_service.add_association(
                        user_id=regular_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    print(f"Superset account created for regular user '{application_user_init_config.user_username}'")
                else:
                    print(f"Warning: Failed to create Superset account for regular user '{application_user_init_config.user_username}'")
                
                users_created.append(application_user_init_config.user_username)
                print(f"Regular user '{application_user_init_config.user_username}' created")
            else:
                print(f"Regular user '{application_user_init_config.user_username}' already exists, skipping...")
            
            if users_created:
                print(f"Successfully created {len(users_created)} user(s): {', '.join(users_created)}")
            else:
                print("No new users were created - all users already exist")
                
            return users_created
            
        except Exception as e:
            print(f"Error creating initial users: {str(e)}")
            raise

    async def _create_keycloak_user(self, user_data: UserCreate) -> str:
        """Create user in Keycloak and return the user ID"""
        try:
            from source.service.keycloak_service import get_keycloak_service
            keycloak_service = get_keycloak_service()
            
            user_id = await keycloak_service.create_user(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                password=user_data.password,
                role=user_data.role.value if user_data.role else "user"
            )
            
            if user_id:
                return user_id
            else:
                raise Exception("Failed to create user in Keycloak")
                
        except Exception as e:
            raise Exception(f"Keycloak user creation failed: {str(e)}")

    async def _update_keycloak_user(self, user_data: UserUpdate) -> bool:
        """Update user in Keycloak"""
        try:
            from source.service.keycloak_service import get_keycloak_service
            keycloak_service = get_keycloak_service()
            
            success = await keycloak_service.update_user(
                user_id=user_data.user_id,
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            
            return success
                
        except Exception as e:
            raise Exception(f"Keycloak user update failed: {str(e)}")

    async def _delete_keycloak_user(self, user_id: str) -> bool:
        """Delete user from Keycloak"""
        try:
            from source.service.keycloak_service import get_keycloak_service
            keycloak_service = get_keycloak_service()
            
            success = await keycloak_service.delete_user(user_id)
            
            return success
                
        except Exception as e:
            raise Exception(f"Keycloak user deletion failed: {str(e)}")

    async def _get_keycloak_user_id(self, username: str) -> str:
        """Get Keycloak user ID by username"""
        try:
            from source.service.keycloak_service import get_keycloak_service
            keycloak_service = get_keycloak_service()
            
            user_id = await keycloak_service.get_user_id_by_username(username)
            
            return user_id
                
        except Exception as e:
            raise Exception(f"Failed to get Keycloak user ID: {str(e)}")