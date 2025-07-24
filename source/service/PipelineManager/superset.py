from typing import Dict, List,Any
from source.service.PipelineManager.interface import BaseStepRunner
from source.config.config import SupersetConfig
from source.service.PipelineManager.supersetclient import SupersetClient
from source.models.user.models import User
import time
from source.schema.user.schemas import UserRole
class SupersetRunner(BaseStepRunner):
    def __init__(self):
        self.container = None 
        self.docker_manager = None  
        self.visualization_container = None
        self.client = None 
        self.username = None
        self.password = None


    def _initialize_superset_client(self,username,password ) -> None:
        """Initialize SupersetClient based on user role"""
        superset_url = SupersetConfig.superset_url
        self.client = SupersetClient(superset_url, username, password)
        if not self.client.authenticate():
            raise RuntimeError("Failed to authenticate with Superset")

    def config(self, step: Dict[str, Any], name: str) -> int:
        """Configure Superset step and return dashboard_id"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot configure.")

        try:
            container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
            step_config = step["config"].step_config
            self.username = SupersetConfig.superset_user
            self.password = SupersetConfig.superset_password
            self._initialize_superset_client(self.username, self.password)

            database = self.client.create_database_if_not_exists(
                database_name=step_config["destination_config"]["database_name"],
                sqlalchemy_uri=step_config["destination_config"]["sqlalchemy_uri"],
                cache_timeout=15,
                expose_in_sqllab=True,
                allow_run_async=False,
                allow_csv_upload=False,
                allow_ctas=False,
                allow_cvas=False,
                allow_dml=False,
                allow_multi_schema_metadata_fetch=False
            )

            if not database:
                raise RuntimeError("Database creation failed or returned None")

            dashboard_title = f"{container_name} Dashboard"
            dashboard_id = self.client.create_dashboard(
                dashboard_title=dashboard_title,
                owners=[SupersetConfig.superset_user_id],
                roles=[SupersetConfig.superset_admin_role_id], 
                published=True
            )

            if not dashboard_id:
                raise RuntimeError("Failed to create dashboard")

            return dashboard_id

        except Exception as e:
            raise RuntimeError(f"Failed to configure Superset: {str(e)}")
        