from typing import Dict, Any, List
from abc import ABC, abstractmethod
from .database_utils import get_table_columns


class TransformationFrameworkHandler(ABC):
    """Abstract base class to handle framework-specific transformation logic."""
    def __init__(self, runner_instance, workdir: str, models_dir: str = "", schema: str = "public", database_connection_params: Dict[str, Any] = None):
        self.runner = runner_instance
        self.workdir = workdir
        self.models_dir = models_dir or f"{workdir}/transform/models"
        self.schema = schema
        self.database_connection_params = database_connection_params

    def generate_model_file_path(self, model_name: str, subfolder: str) -> str:
        """Generate the file path for a model file."""
        return f"{self.models_dir}/{subfolder}/{model_name}.sql"

    @abstractmethod
    def create_model_file_content(self, model_name: str, sql_content: str) -> str:
        pass

    @abstractmethod
    def format_source_table_reference(self, table_name: str, schema_name: str) -> str:
        pass
        
    @abstractmethod
    def format_model_reference(self, model_name: str) -> str:
        pass

    def get_table_columns(self, table_name: str, schema: str) -> List[str]:
        return get_table_columns(table_name, schema, self.database_connection_params)
            
    def write_model_file(self, model_name: str, sql_content: str, subfolder: str):
        """Creates the directory and writes the model file."""
        model_path = self.generate_model_file_path(model_name, subfolder)
        full_content = self.create_model_file_content(model_name, sql_content)
        
        directory = '/'.join(model_path.split('/')[:-1])
        self.runner.docker_manager.exec_command(
            command=["sh", "-c", f"mkdir -p {directory}"],
            workdir=self.workdir
        )        
        escaped_content = full_content.replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
        self.runner.docker_manager.exec_command(
            command=["sh", "-c", f"printf '%s\\n' \"{escaped_content}\" > {model_path}"],
            workdir=self.workdir
        ) 