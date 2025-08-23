from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from source.schema.user.schemas import UserRole

class DatabaseConfig(BaseSettings):
    DB_HOST: str = Field(env="DB_HOST", default="postgres")
    DB_PORT: int = Field(env="DB_PORT", default=5432)
    DB_USER: str = Field(env="DB_USER", default="user")
    DB_PASSWORD: str = Field(env="DB_PASSWORD", default="password")
    DB_NAME: str = Field(env="DB_NAME", default="mydatabase")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

class AuthConfig(BaseSettings):
    secret_key: str = Field(env="secret_key", default="wissem")
    algorithm: str = Field(env="algorithm", default="HS256")
    token_expiry_minutes: int = Field(env="token_expiry_minutes", default=30)
    version: str = Field(env="version", default="V1")

class KeycloakConfig(BaseSettings):
    keycloak_url: str = Field(env="KEYCLOAK_URL", default="http://keycloak:8080")
    keycloak_external_url: str = Field(env="KEYCLOAK_EXTERNAL_URL", default="http://localhost:8080")
    keycloak_realm: str = Field(env="KEYCLOAK_REALM", default="pipeline-realm")
    client_id: str = Field(env="KEYCLOAK_CLIENT_ID", default="fastapi-client")
    client_secret: str = Field(env="KEYCLOAK_CLIENT_SECRET", default="your-client-secret-here")
    admin_username: str = Field(env="KEYCLOAK_ADMIN_USERNAME", default="admin")
    admin_password: str = Field(env="KEYCLOAK_ADMIN_PASSWORD", default="admin")
    redirect_uris: List[str] = Field(env="KEYCLOAK_REDIRECT_URIS", default=["http://localhost:3000/*", "http://localhost:3001/*"])
    web_origins: List[str] = Field(env="KEYCLOAK_WEB_ORIGINS", default=["http://localhost:3000", "http://localhost:3001"])
    realm_display_name: str = Field(env="KEYCLOAK_REALM_DISPLAY_NAME", default="Pipeline Realm")
    
    @property
    def admin_realm(self) -> str:
        return "master"
    
    @property 
    def app_realm(self) -> str:
        return self.keycloak_realm
    
    @property
    def server_url(self) -> str:
        return self.keycloak_url
    
    @property
    def realm_name(self) -> str:
        return self.keycloak_realm

class GitHubConfig(BaseSettings):
    github_token: str = Field(env="github_token", default="your-github-token-here")
    github_username: str = Field(env="github_username", default="wissemHammoudi1")
    github_email: str = Field(env='github_email', default="wissem.hammoudi@elyadata.com")

class DockerConfig(BaseSettings):
    meltano_docker_image: str = Field(env="meltano_docker_image", default="wissem020/meltano")
    dlt_sqlmesh_superset_docker_image: str = Field(env="dlt_sqlmesh_superset_docker_image", default="wissem020/sqlmesh_dlt_superset")
    Docker_Client_Base_Url: str = Field(env="Docker_Client_Base_Url", default="unix://var/run/docker.sock")

class SupersetConfig(BaseSettings):
    superset_secret_key: str = Field(env="superset_secret_key", default="your-superset-secret-key-here")
    superset_user: str = Field(env="superset_user", default="admin")
    superset_password: str = Field(env="superset_password", default="your-superset-password-here")
    superset_sqlalchemy_uri: str = Field(env="superset_sqlalchemy_uri", default="postgresql://user:password@postgres:5432/postgres")
    superset_url: str = Field(env="superset_url", default="http://superset:8088")
    superset_user_url: str = Field(env="superset_url", default="http://localhost:8088")
    superset_user_id: int = Field(env="superset_user_id", default=1)
    superset_admin_role_id: int = Field(env="superset_admin_role_id", default=1)
    superset_gamma_role_id: int = Field(env="superset_gamma_role_id", default=4)

class APIConfig(BaseSettings):
    api_prefix: str = Field(env="api_prefix", default="/api/v1")
    base_url: str = Field(env="base_url", default="/api/v1")
    frontend_url: str = Field(env="frontend_url", default="http://frontend:3000")
    frontend_url_develop: str = Field(env="frontend_url_develop", default="http://localhost:3000")

class ApplicationUserInitConfig(BaseSettings):
    admin_username: str = Field(env="admin_username", default="admin123")
    admin_email: str = Field(env="admin_email", default="admin@example.com")
    admin_password: str = Field(env="admin_password", default="admin123")
    admin_role: str = Field(env="admin_role", default="admin")
    admin_first_name: str = Field(env="admin_first_name", default="Admin")
    admin_last_name: str = Field(env="admin_last_name", default="Admin")
    
    user_username: str = Field(env="user_username", default="user123")
    user_email: str = Field(env="user_email", default="user@example.com")
    user_password: str = Field(env="user_password", default="user123")
    user_role: str = Field(env="user_role", default="user")
    user_first_name: str = Field(env="user_first_name", default="Regular")
    user_last_name: str = Field(env="user_last_name", default="User")
    
    demo_users: List[Dict[str, str]] = Field(env="demo_users", default=[
        {
            "username": "user",
            "email": "user@example.com",
            "first_name": "Regular",
            "last_name": "User",
            "password": "user123",
            "role": "user"
        }
    ])


class ExternalServicesConfig(BaseSettings):
    n8n_webhook_Url: str = Field(env="n8n_webhook_Url", default="http://n8n:5678/webhook/sql-transformation")
    
# Configuration instances
application_user_init_config = ApplicationUserInitConfig()
external_services_config = ExternalServicesConfig()
api_config = APIConfig()
superset_config = SupersetConfig()
database_config = DatabaseConfig()
auth_config = AuthConfig()
github_config = GitHubConfig()
docker_config = DockerConfig()
keycloak_config = KeycloakConfig()
user_config = ApplicationUserInitConfig()  