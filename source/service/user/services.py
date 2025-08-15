from source.schema.user.schemas import UserCreate, UserUpdate, PasswordUpdate, LoginSchema
from source.models.user.models import User
from source.repository.user.repository import UserRepository
from source.exceptions.exceptions import UserNotFoundError, DuplicateUserError, InvalidPasswordError
from source.service.authentication.service import AuthService  
from source.config.config import AuthConfig, SupersetConfig, ApplicationUserInitConfig
from source.service.PipelineManager.supersetclient import SupersetClient
from source.service.user_superset_account_association.service import UserSupersetAccountAssociationService
from source.schema.user.schemas import UserRole
auth_service_instance = AuthService(
    user_repo=UserRepository(),
    secret_key=AuthConfig.secret_key,  
    algorithm=AuthConfig.algorithm,
    token_expiry_minutes=AuthConfig.token_expiry_minutes)

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.auth_service = auth_service_instance
        self.user_superset_account_association_service = UserSupersetAccountAssociationService()
        self.superset_client = SupersetClient(
            base_url=SupersetConfig.superset_url,
            username=SupersetConfig.superset_user,
            password=SupersetConfig.superset_password
        )
    def signup(self, user_data: UserCreate):
        if self.user_repository.get_user_by_email_and_username(user_data.email, user_data.username, ):
            raise DuplicateUserError("Username or email already exists")
        user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        user.password_hash = self.auth_service.hash_password(password=user_data.password)
        self.user_repository.create_user(user, )
        user_id = user.user_id
        if user_data.role == UserRole.admin:
            superset_roles = [SupersetConfig.superset_admin_role_id]
        else:
            superset_roles = [SupersetConfig.superset_gamma_role_id]
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
            self.user_superset_account_association_service.add_association(user_id=user_id, superset_user_id=superset_user_id)
        if not superset_user_id:
            return {"message": "User has been created successfully, but Superset account creation failed", "user_id": user_id}
        return {"message": "User has been created successfully", "user_id": user_id}

    def get_all_users(self):
        return self.user_repository.get_all_active_user()
    
    def get_user_by_id(self,user_id:int ):
        return self.user_repository.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str):
        user = self.user_repository.get_active_user_by_username(username, )
        if not user:
            raise UserNotFoundError(f"User with username '{username}' not found")
        return user

    def delete_user(self, user_id: int):
        user = self.user_repository.get_active_user_by_id(user_id, )
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        self.user_repository.mark_deleted(user, )

    def update_password(self, password_data: PasswordUpdate):
        user = self.user_repository.get_active_user_by_id(password_data.user_id, )
        if not user:
            raise UserNotFoundError(f"User with ID {password_data.user_id} not found")
        if not self.auth_service.verify_password(password_data.old_password, user.password_hash):
            raise InvalidPasswordError("Old password is incorrect")
        user.password_hash = self.auth_service.hash_password(password=password_data.new_password)
        self.user_repository.commit()
        return {"message": "Password updated successfully"}

    def update_user(self, user_data: UserUpdate):
        user = self.user_repository.get_user_by_id(user_data.user_id, )
        if not user:
            raise UserNotFoundError(f"User with ID {user_data.user_id} not found")
        if user_data.email:
            existing_email = self.user_repository.get_user_by_email(user_data.email, )
            if existing_email and existing_email.user_id != user.user_id:
                raise DuplicateUserError("Email already exists")
            user.email = user_data.email
        if user_data.username:
            existing_username = self.user_repository.get_user_by_username(user_data.username, )
            if existing_username and existing_username.user_id != user.user_id:
                raise DuplicateUserError("Username already exists")
            user.username = user_data.username
        if user_data.first_name:
            user.first_name = user_data.first_name
        if user_data.last_name:
            user.last_name = user_data.last_name
        self.user_repository.commit()
        return {"message": "User information updated successfully"}

    def login(self, login_data: LoginSchema):
        user = self.user_repository.get_active_user_by_username(login_data.username)
        if not user or not self.auth_service.verify_password(login_data.password, user.password_hash):
            raise InvalidPasswordError("Invalid username or password")

        access_token = self.auth_service.create_access_token(user)
        return {"access_token": access_token, "token_type": "bearer"}

    def create_initial_users(self):
        """Create admin and regular user if they don't exist"""
        users_created = []
        
        try:
            admin_user = self.user_repository.get_user_by_username(ApplicationUserInitConfig.admin_username)
            if not admin_user:
                admin_user = User(
                    username=ApplicationUserInitConfig.admin_username,
                    email=ApplicationUserInitConfig.admin_email,
                    first_name=ApplicationUserInitConfig.admin_username,
                    last_name=ApplicationUserInitConfig.admin_username,
                    password_hash=self.auth_service.hash_password(ApplicationUserInitConfig.admin_password),
                    role=ApplicationUserInitConfig.admin_role
                )
                self.user_repository.create_user(admin_user)
                
                superset_roles = [SupersetConfig.superset_admin_role_id]
                superset_user_id = self.superset_client.create_user(
                    username=ApplicationUserInitConfig.admin_username,
                    email=ApplicationUserInitConfig.admin_email,
                    first_name="Admin",
                    last_name="User",
                    password=ApplicationUserInitConfig.admin_username,  
                    roles=superset_roles,
                    active=True
                )
                
                if superset_user_id:
                    self.user_superset_account_association_service.add_association(
                        user_id=admin_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    print(f"Superset account created for admin user '{ApplicationUserInitConfig.admin_username}'")
                else:
                    print(f"Warning: Failed to create Superset account for admin user '{ApplicationUserInitConfig.admin_username}'")
                
                users_created.append(ApplicationUserInitConfig.admin_username)
                print(f"Admin user '{ApplicationUserInitConfig.admin_username}' created")
            else:
                print(f"Admin user '{ApplicationUserInitConfig.admin_username}' already exists, skipping...")
            
            regular_user = self.user_repository.get_user_by_username(ApplicationUserInitConfig.user_username)
            if not regular_user:
                regular_user = User(
                    username=ApplicationUserInitConfig.user_username,
                    email=ApplicationUserInitConfig.user_email,
                    first_name=ApplicationUserInitConfig.user_username,
                    last_name=ApplicationUserInitConfig.user_username,
                    password_hash=self.auth_service.hash_password(ApplicationUserInitConfig.user_password),
                    role=ApplicationUserInitConfig.user_role
                )
                self.user_repository.create_user(regular_user)
                
                superset_roles = [SupersetConfig.superset_gamma_role_id]
                superset_user_id = self.superset_client.create_user(
                    username=ApplicationUserInitConfig.user_username,
                    email=ApplicationUserInitConfig.user_email,
                    first_name="Regular",
                    last_name="User",
                    password=ApplicationUserInitConfig.user_username,  
                    roles=superset_roles,
                    active=True
                )
                
                if superset_user_id:
                    self.user_superset_account_association_service.add_association(
                        user_id=regular_user.user_id, 
                        superset_user_id=superset_user_id
                    )
                    print(f"Superset account created for regular user '{ApplicationUserInitConfig.user_username}'")
                else:
                    print(f"Warning: Failed to create Superset account for regular user '{ApplicationUserInitConfig.user_username}'")
                
                users_created.append(ApplicationUserInitConfig.user_username)
                print(f"Regular user '{ApplicationUserInitConfig.user_username}' created")
            else:
                print(f"Regular user '{ApplicationUserInitConfig.user_username}' already exists, skipping...")
            
            if users_created:
                print(f"Successfully created {len(users_created)} user(s): {', '.join(users_created)}")
            else:
                print("No new users were created - all users already exist")
                
            return users_created
            
        except Exception as e:
            print(f"Error creating initial users: {str(e)}")
            raise