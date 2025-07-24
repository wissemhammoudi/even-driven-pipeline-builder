from typing import Dict, Any
from source.service.PipelineManager.interface import BaseStepRunner
from source.service.PipelineManager.transfomrationManager.transformation_manager import TransformationManager

class SqlmeshRunner(BaseStepRunner):
    def __init__(self):
        self.container = None  
        self.docker_manager = None  

    def config(self, step: Dict[str, Any], name: str) -> None:
        """Configure SQLMesh pipeline step"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot configure.")
            
        try:
            step_config = step["config"].step_config
            container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
            workdir = f"/project/{container_name}"
            models_dir = f"{workdir}/models"
            test_dir = f"{workdir}/tests"
            macros_dir = f"{workdir}/macros"            
            self.docker_manager.exec_command(
                command=["sh", "-c", f"mkdir -p {workdir}"],
                workdir="/"
            )
            commands = [
                ["sqlmesh", "init", step_config["dialect"]],
                ["sh", "-c", f"rm -f {models_dir}/*.sql"],
                ["sh", "-c", f"rm -f {test_dir}/*.yaml"],
                ["sh", "-c", f"mkdir -p {models_dir}/staging"],
                ["sh", "-c", f"mkdir -p {models_dir}/agentic"],
                ["cp", "/project/handle_column_transformation.sql", f"{macros_dir}/"]
            ]
            for command in commands:
                self.docker_manager.exec_command(
                    command=command,
                    workdir=workdir
                )            
            destination = step_config["destination"]
            destination_config = step_config["destination_config"]
            for config_key, config_value in destination_config.items():
                if config_key=="schema":
                    continue
                self.docker_manager.exec_command(
                    command=[
                        "sh", "-c",
                        f"yq -y --in-place '.gateways.{destination}.connection.{config_key} = \"{config_value}\"' config.yaml"
                    ],
                    workdir=workdir
                )
            transformation_manager = TransformationManager(self.docker_manager, workdir, models_dir)
            transformation_manager.configure_table_sync(step_config, framework="sqlmesh")
        except Exception as e:
            raise RuntimeError(f"Error configuring SQLMesh: {str(e)}")

    def start(self, step: Dict[str, Any], name: str) -> None:
        """Start the SQLMesh pipeline execution"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot start.")
            
        try:
            container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
            workdir = f"/project/{container_name}"
            self.docker_manager.exec_command(
                command=["sqlmesh", "plan", "--auto-apply"],
                workdir=workdir
            )
            self.docker_manager.exec_command(
                command=["sqlmesh", "run"],
                workdir=workdir
            )

        except Exception as e:
            raise RuntimeError(f"Error running SQLMesh pipeline: {str(e)}")
