from pydantic_settings import BaseSettings
from pydantic import Field

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

class GitHubConfig(BaseSettings):
    github_token: str = Field(env="github_token", default=" test_token")
    github_username: str = Field(env="github_username", default="wissemHammoudi1")
    github_email: str = Field(env='github_email', default="wissem.hammoudi@elyadata.com")

class DockerConfig(BaseSettings):
    meltano_docker_image: str = Field(env="meltano_docker_image", default="wissem020/meltano")
    dlt_sqlmesh_superset_docker_image: str = Field(env="dlt_sqlmesh_superset_docker_image", default="wissem020/sqlmesh_dlt_superset")
    Docker_Client_Base_Url: str = Field(env="Docker_Client_Base_Url", default="unix://var/run/docker.sock")

class SupersetConfig(BaseSettings):
    superset_secret_key: str = Field(env="superset_secret_key", default="test_secret_key")
    superset_user: str = Field(env="superset_user", default="admin")
    superset_password: str = Field(env="superset_password", default="  admin")
    superset_sqlalchemy_uri: str = Field(env="superset_sqlalchemy_uri", default="postgresql://user:password@postgres:5432/postgres")
    superset_url: str = Field(env="superset_url", default="http://superset:8088")
    superset_user_id: int = Field(env="superset_user_id", default=1)
    superset_admin_role_id: int = Field(env="superset_admin_role_id", default=1)
    superset_gamma_role_id: int = Field(env="superset_gamma_role_id", default=4)

class APIConfig(BaseSettings):
    api_prefix: str = Field(env="api_prefix", default="/api/v1")
    base_url: str = Field(env="base_url", default="/api/v1")
    frontend_url: str = Field(env="frontend_url", default="http://frontend:3000")
    frontend_url_develop: str = Field(env="frontend_url_develop", default="http://localhost:3000")

class ExternalServicesConfig(BaseSettings):
    transformation_agent_Url: str = Field(env="transformation_agent_Url", default="http://n8n:5678/webhook/sql-transformation")

class EmailConfig(BaseSettings):
    smtp_server: str = Field(env="EMAIL_SMTP_SERVER", default="smtp.gmail.com")
    smtp_port: int = Field(env="EMAIL_SMTP_PORT", default=587)
    smtp_username: str = Field(env="EMAIL_SMTP_USERNAME", default="wissham25@gmail.com")
    smtp_password: str = Field(env="EMAIL_SMTP_PASSWORD", default="your_password_here")
    use_tls: bool = Field(env="EMAIL_USE_TLS", default=True)

ExternalServicesConfig = ExternalServicesConfig()
APIConfig = APIConfig()
SupersetConfig = SupersetConfig()
DatabaseConfig = DatabaseConfig()
AuthConfig = AuthConfig()
GitHubConfig = GitHubConfig()
DockerConfig = DockerConfig()
EmailConfig = EmailConfig()
