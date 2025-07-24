from typing import Dict, Any
import time
import yaml
from source.service.PipelineManager.interface import BaseStepRunner
from source.schema.pipeline.schema import StepTypeEnum
from source.service.PipelineManager.supersetclient import SupersetClient
from source.config.config import SupersetConfig
from source.service.PipelineManager.transfomrationManager.transformation_manager import TransformationManager
from source.models.user.models import User


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
        
        # Initialize Meltano project
        self.docker_manager.exec_command(
            command=["sh", "-c", f"if [ ! -d '{workdir}' ]; then meltano init {container_name}; fi"],
        )  
        # Add and configure extractor
        extractor_type = step_config['extractor_type']
        loader_type = step_config['loader_type']

        self.docker_manager.exec_command(
            command=f"meltano add extractor {extractor_type}",
            workdir=workdir
        )
        for conf, value in step_config["connection_config"]["extractor"].items():
            if isinstance(value, (int, float)):
                config_value = str(value)
            else:
                config_value = f"'{value}'" if ' ' in value else value
                
            self.docker_manager.exec_command(
                command=f"meltano config {extractor_type} set {conf} {config_value}",
                workdir=workdir
            )
        # Add and configure loader
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
        
        # Configure table selections
        schema = step_config['connection_config']['extractor']['filter_schemas'][0]
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
        
        # Check if container folder exists, if not initialize Meltano project
        self.docker_manager.exec_command(
            command=["sh", "-c", f"if [ ! -d '{workdir}' ]; then meltano init {container_name}; fi"],
        )
        
        # Add and configure utility
        self.docker_manager.exec_command(
            command=f"meltano add utility {utility_type}",
            workdir=workdir
        )
        for conf, value in step_config["destination_config"].items():
            self.docker_manager.exec_command(
                command=f"meltano config {utility_type} set {conf} {value}",
                workdir=workdir
            )
        
        # Initialize utility
        self.docker_manager.exec_command(
            command=f"meltano invoke {utility_type}:initialize",
            workdir=workdir
        )
        
        # Configure dbt project
        self.docker_manager.exec_command(
            command=["sh", "-c", f"sed -i 's#\\.\\./\\.meltano/transformers/dbt/target#./.meltano/transformers/dbt/target#g' {workdir}/transform/dbt_project.yml"],
            workdir=workdir
        )
        
        # Create directories and files
        self.docker_manager.exec_command(
            command=["sh", "-c", f"mkdir -p {workdir}/transform/macros"],
            workdir=workdir
        )
        self.docker_manager.exec_command(
            command=["sh", "-c", f"mkdir -p {workdir}/transform/models/sources"],
            workdir=workdir
        )
        self.docker_manager.exec_command(
            command=["sh", "-c", f"mkdir -p {workdir}/transform/models/staging"],
            workdir=workdir
        )
        self.docker_manager.exec_command(
            command=["sh", "-c", f"mkdir -p {workdir}/transform/models/agentic"],
            workdir=workdir
        )

        # Copy transformation macro
        self.docker_manager.exec_command(
            command=["sh", "-c", f"cp /project/handle_column_transformation.sql {workdir}/transform/macros"],
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
                self.docker_manager.exec_command(
                    command=f"meltano config {extractor_type} set password {extractor_password}",
                    workdir=workdir
                )
                self.docker_manager.exec_command(
                    command=f"meltano config {loader_type} set password {loader_password}",
                    workdir=workdir
                )
                self.docker_manager.exec_command(
                    command=f"meltano run {step_config['extractor_type']} {step_config['loader_type']}",
                    workdir=workdir
                )
                
            elif step_config["config_type"] == StepTypeEnum.DATA_TRANSFORMATION:
                password = step_config["destination_config"]["password"]
                self.docker_manager.exec_command(
                    command=f"meltano config {step_config['utility_type']} set password {password}",
                    workdir=workdir
                )
                self.docker_manager.exec_command(
                    command="meltano invoke dbt-postgres:run",
                    workdir=workdir
                )
                
        except Exception as e:
            raise RuntimeError(f"Error running Meltano: {str(e)}")

    def start_visualization(self, config: Dict[str, Any], name: str, user: User) -> Dict[str, Any]:
        """Start Superset visualization"""
        try:
            container_name = f"{name.split('_')[1]}_{name.split('_')[2]}"
            workdir = f"/project/{container_name}"
            step_config = config.step_config
            
            if user.role.upper() == 'ADMIN':
                username = SupersetConfig.superset_user
                password = SupersetConfig.superset_password
            else:
                username = user.username
                password = "123456789"
                
            # Initialize client first
            client = SupersetClient(
                SupersetConfig.superset_url,  
                username,
                password
            )
            
            if not client.authenticate():
                raise RuntimeError("Failed to authenticate with Superset")

            # Now we can use client
            user_id = client.get_user_id(username)

            schema = step_config["destination_config"]["schema"]
            
            # Get the database ID dynamically instead of hardcoding to 1
            databases = client.get_databases()
            if not databases or not databases.get('result'):
                raise RuntimeError("No databases found in Superset")
            
            # Find the database by name from step config
            database_name = step_config["destination_config"]["database_name"]
            database_id = None
            for db in databases['result']:
                if db.get('database_name') == database_name:
                    database_id = db.get('id')
                    break
            
            if not database_id:
                raise RuntimeError(f"Database '{database_name}' not found in Superset")
                
            # Invalidate cache for both schemas to ensure fresh data
            client._invalidate_table_cache(database_id=database_id, schema_name=schema)
            client._invalidate_table_cache(database_id=database_id, schema_name=f"sqlmesh__{schema}")

            # Get tables from the original schema
            tables_original_schema = client.get_database_tables(
                database_id=database_id,
                schema_name=schema,
                force=True,
                invalidate_cache_first=False
            )

            # Get tables from the sqlmesh schema
            tables_sqlmesh_schema = client.get_database_tables(
                database_id=database_id,
                schema_name=f"sqlmesh__{schema}",
                force=True,
                invalidate_cache_first=False
            )

            if not tables_original_schema or not tables_original_schema.get('result'):
                print(f"Warning: No tables found in schema '{schema}'")
                tables_original_schema = {'result': []}

            if not tables_sqlmesh_schema or not tables_sqlmesh_schema.get('result'):
                print(f"Warning: No tables found in schema 'sqlmesh__{schema}'")
                tables_sqlmesh_schema = {'result': []}

            superset_prefixes = [
                'ab_', 'alembic_', 'cache_', 'css_', 'dashboard', 
                'dbs', 'dynamic_', 'embedded_', 'favstar', 
                'key_value', 'keyvalue', 'logs', 'query', 
                'report_', 'rls_', 'row_level_', 'saved_', 
                'slice', 'sql_', 'ssh_', 'tab_', 'table_', 
                'tables', 'tag', 'user_', 'annotation',
                'sqlatable_user', 'database_user_oauth2_tokens', 'filter_sets',
                "sl_columns","sl_dataset_columns","sl_dataset_tables","sl_dataset_users"
            ]

            user_tables_original = [
                table for table in tables_original_schema['result']
                if not any(table['value'].startswith(prefix) for prefix in superset_prefixes)
            ]

            user_tables_sqlmesh = [
                table for table in tables_sqlmesh_schema['result']
                if not any(table['value'].startswith(prefix) for prefix in superset_prefixes)
            ]

            all_tables_to_map = []
            for table in user_tables_original:
                all_tables_to_map.append({'table_name': table['value'], 'schema': schema})
            for table in user_tables_sqlmesh:
                all_tables_to_map.append({'table_name': table['value'], 'schema': f"sqlmesh__{schema}"})
            
            if not user_id:
                raise RuntimeError(f"Failed to get user ID for user: {username}")

            if not all_tables_to_map:
                print("No user-defined tables found in any schema to map.")
            else:
                print(f"Attempting to map {len(all_tables_to_map)} tables from schemas: '{schema}' and 'sqlmesh__{schema}'...")
                for table_info in all_tables_to_map:
                    try:
                        dataset = client.create_dataset_if_not_exists(
                            table_name=table_info['table_name'],
                            database_id=database_id,  # Use dynamic database_id
                            schema=table_info['schema'],
                            owners=[user_id]  # Use dynamic user_id
                        )
                        if dataset:
                            print(f"Successfully mapped table: {table_info['table_name']} in schema: {table_info['schema']}")
                        else:
                            print(f"Warning: Failed to map table: {table_info['table_name']} in schema: {table_info['schema']}")
                    except Exception as e:
                        print(f"Error mapping table {table_info['table_name']} in schema {table_info['schema']}: {str(e)}")
                        continue

            return {
                "status": "started",
                "visualization_url": f"{SupersetConfig.superset_url}",
                "username": username,
                "password": password,
            }

        except Exception as e:
            raise RuntimeError(f"Error starting visualization pipeline: {str(e)}")
