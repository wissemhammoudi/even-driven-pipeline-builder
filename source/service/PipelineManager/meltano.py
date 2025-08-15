from typing import Dict, Any
import time
import yaml
from source.service.PipelineManager.interface import BaseStepRunner
from source.schema.pipeline.schema import StepTypeEnum, DatabaseConfigurationEnum
from source.service.PipelineManager.transfomrationManager.transformation_manager import TransformationManager


class MeltanoRunner(BaseStepRunner):
    def __init__(self):
        self.container = None  
        self.docker_manager = None  

    def config(self, step: Dict[str, Any], name: str) -> None:
        """Configure Meltano step based on step type"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot configure.")            
        container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"      
        step_config = step["config"].step_config
        workdir = f"/project/{container_name}"  

        try:
            if step_config["config_type"] == StepTypeEnum.DATA_INGESTION:
                self._configure_data_ingestion(step, container_name, workdir)
            elif step_config["config_type"] == StepTypeEnum.DATA_TRANSFORMATION:
                self._configure_data_transformation(step, container_name, workdir)

                
        except Exception as e:
            raise RuntimeError(f"Error configuring Meltano: {str(e)}")

    def _configure_data_ingestion(self, step: Dict[str, Any], container_name: str, workdir: str) -> None:
        """Configure data ingestion step"""
        step_config = step["config"].step_config
        
        self.docker_manager.exec_command(
            command=["sh", "-c", f"if [ ! -d '{workdir}' ]; then meltano init {container_name}; fi"],
        )  
        extractor_type = step_config['extractor_type']
        loader_type = step_config['loader_type']

        self.docker_manager.exec_command(
            command=f"meltano add extractor {extractor_type}",
            workdir=workdir
        )
        for conf, value in step_config["connection_config"]["extractor"].items():
            if conf == 'schema':
                conf = 'filter_schemas'
                if isinstance(value, list):
                    config_value = str(value)
                else:
                    config_value = str([value]) 
            elif isinstance(value, (int, float)):
                config_value = str(value)
            else:
                config_value = f"'{value}'" if ' ' in value else value
                
            self.docker_manager.exec_command(
                command=f"meltano config {extractor_type} set {conf} {config_value}",
                workdir=workdir
            )
        self.docker_manager.exec_command(
            command=f"meltano add loader {loader_type}",
            workdir=workdir
        )        
        for conf, value in step_config["connection_config"]["loader"].items():
            if isinstance(value, (int, float)):
                config_value = str(value)
            else:
                config_value = f"'{value}'" if ' ' in value else value
                
            self.docker_manager.exec_command(
                command=f"meltano config {loader_type} set {conf} {config_value}",
                workdir=workdir
            )
        
        schema = step_config['connection_config']['extractor']['schema']
        selected_table = step_config["table_sync_config"]
        for table, columns in selected_table.items():
            qualified_table = f"{schema}-{table}"
            for col in columns:
                self.docker_manager.exec_command(
                    command=f"meltano select {extractor_type} {qualified_table} {col['column']}",
                    workdir=workdir
                )

    def _configure_data_transformation(self, step: Dict[str, Any], container_name: str, workdir: str) -> None:
        """Configure data transformation step"""
        step_config = step["config"].step_config
        utility_type = step_config['utility_type']
        
        self.docker_manager.exec_command(
            command=["sh", "-c", f"if [ ! -d '{workdir}' ]; then meltano init {container_name}; fi"],
        )
        utility_commands = [f"meltano add utility {utility_type}"]        
        for conf, value in step_config["destination_config"].items():
            if conf == DatabaseConfigurationEnum.database:
                conf = DatabaseConfigurationEnum.dbname
            utility_commands.append(f"meltano config {utility_type} set {conf} {value}")
        utility_commands.append(f"meltano invoke {utility_type}:initialize")        
        for command in utility_commands:
            self.docker_manager.exec_command(
                command=command,
                workdir=workdir
            )  
        setup_commands = [
            ["sh", "-c", f"sed -i 's#\\.\\./\\.meltano/transformers/dbt/target#./.meltano/transformers/dbt/target#g' {workdir}/transform/dbt_project.yml"],
            ["sh", "-c", f"mkdir -p {workdir}/transform/macros"],
            ["sh", "-c", f"mkdir -p {workdir}/transform/models/sources"],
            ["sh", "-c", f"mkdir -p {workdir}/transform/models/staging"],
            ["sh", "-c", f"mkdir -p {workdir}/transform/models/agentic"],
            ["sh", "-c", f"cp /project/handle_column_transformation.sql {workdir}/transform/macros"]
        ]        
        for command in setup_commands:
            self.docker_manager.exec_command(
                command=command,
                workdir=workdir
            )
        models_dir = f"{workdir}/transform/models"
        transformation_manager = TransformationManager(self.docker_manager, workdir, models_dir)
        transformation_manager.configure_table_sync(step_config, framework="dbt")

    def start(self, step: Dict[str, Any], name: str) -> None:
        """Start the Meltano step execution"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot start.")
            
        container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
        step_config = step["config"].step_config
        workdir = f"/project/{container_name}"
        
        try:
            if step_config["config_type"] == StepTypeEnum.DATA_INGESTION:
                extractor_type = step_config['extractor_type']
                loader_type = step_config['loader_type']
                extractor_password = step_config['connection_config']['extractor']['password']
                loader_password = step_config['connection_config']['loader']['password']                
                ingestion_commands = [
                    f"meltano config {extractor_type} set password {extractor_password}",
                    f"meltano config {loader_type} set password {loader_password}",
                    f"meltano run {step_config['extractor_type']} {step_config['loader_type']}"
                ]            
                for command in ingestion_commands:
                    self.docker_manager.exec_command(
                        command=command,
                        workdir=workdir
                    )
                
            elif step_config["config_type"] == StepTypeEnum.DATA_TRANSFORMATION:
                password = step_config["destination_config"]["password"]                
                transformation_commands = [
                    f"meltano config {step_config['utility_type']} set password {password}",
                    "meltano invoke dbt-postgres:run"
                ]                
                for command in transformation_commands:
                    self.docker_manager.exec_command(
                        command=command,
                        workdir=workdir
                    )
                
        except Exception as e:
            raise RuntimeError(f"Error running Meltano: {str(e)}")
