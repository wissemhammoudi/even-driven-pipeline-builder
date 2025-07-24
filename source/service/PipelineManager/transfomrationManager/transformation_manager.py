from typing import Dict, Any, List
import yaml
import re
from source.service.PipelineManager.transfomrationManager.base_handler import TransformationFrameworkHandler
from source.service.PipelineManager.transfomrationManager.sqlmesh_handler import SQLMeshHandler
from source.service.PipelineManager.transfomrationManager.dbt_handler import DBTHandler

DEFAULT_SCHEMA = "public"
DEFAULT_PORT = 5432
DEFAULT_JOIN_TYPE = "LEFT"
MIN_WORD_LENGTH = 4
MAX_KEYWORDS = 4
DATABASE_PARAM_KEYS = ["host", "dbname", "database", "user", "username", "password"]


class TransformationManager:
    """Manages all transformation-related operations for data pipelines."""
    
    def __init__(self, runner_instance, workdir: str, models_dir: str):
        self.runner = runner_instance
        self.workdir = workdir
        self.models_dir = models_dir
    
    def get_framework_handler(self, framework: str, step_config: Dict[str, Any]) -> TransformationFrameworkHandler:
        """Factory function to get the correct framework handler."""
        database_params = {}
        if step_config.get("source_config"):
            database_params = step_config.get("source_config", {})
        elif step_config.get("connection_config", {}).get("source"):
            database_params = step_config.get("connection_config", {}).get("source", {})
        elif step_config.get("connection_config", {}).get("extractor"):
            database_params = step_config.get("connection_config", {}).get("extractor", {})
        else:
            for key, value in step_config.items():
                if isinstance(value, dict) and any(param in value for param in DATABASE_PARAM_KEYS):
                    database_params = value
                    break
        
        normalized_connection_params = {}
        if database_params:
            param_mapping = {
                "host": "host",
                "port": "port", 
                "database": "dbname",
                "dbname": "dbname",
                "user": "user",
                "username": "user",
                "password": "password"
            }
            
            for old_key, new_key in param_mapping.items():
                if old_key in database_params and database_params[old_key]:
                    normalized_connection_params[new_key] = database_params[old_key]            
            if "port" in normalized_connection_params:
                try:
                    normalized_connection_params["port"] = int(normalized_connection_params["port"])
                except (ValueError, TypeError):
                    normalized_connection_params["port"] = DEFAULT_PORT
        
        schema = step_config.get("destination_config", {}).get("schema", DEFAULT_SCHEMA)
        
        if framework.lower() == "dbt":
            return DBTHandler(self.runner, self.workdir, self.models_dir, schema, normalized_connection_params)
        elif framework.lower() == "sqlmesh":
            return SQLMeshHandler(self.runner, self.workdir, self.models_dir, schema, normalized_connection_params)
        raise ValueError(f"Unsupported framework: {framework}")

    def configure_table_sync(self, step_config: Dict[str, Any], framework: str = "sqlmesh") -> None:
        """Configure table synchronization models for SQLMesh or dbt."""
        framework_handler = self.get_framework_handler(framework, step_config)
        
        table_sync_details = self._standardize_table_sync_configuration(step_config.get("table_sync_config", {}))
        column_transformations_config = step_config.get("column_functions", {})
        agentic_transformations = step_config.get("agentic_transformations", [])
        join_transformations = step_config.get("join_transformations", [])

        if framework.lower() == "dbt":
            self._generate_dbt_sources(framework_handler, table_sync_details)

        for table_configuration in table_sync_details:
            model_name = f"stg_{table_configuration['schema_name']}__{table_configuration['table_name']}"
            sql_content = self._build_staging_model_select_clause(framework_handler, table_configuration, column_transformations_config)
            framework_handler.write_model_file(model_name, sql_content, "staging")

        for transformation_index, join_config in enumerate(join_transformations):
            model_name = join_config.get("name", f"join_transformation_{transformation_index + 1}")
            sql_content = self._build_join_transformation_sql(framework_handler, join_config)
            if sql_content:
                framework_handler.write_model_file(model_name, sql_content, "joins")
                
        for transformation_index, agentic_config in enumerate(agentic_transformations):
            raw_sql = agentic_config.get("result", "").strip()
            if not raw_sql:
                continue
            
            cleaned_sql = self._sanitize_and_validate_agentic_sql(raw_sql, framework)
            model_name = self._create_model_name_from_transformation_intent(agentic_config.get("intent", ""), transformation_index)
            framework_handler.write_model_file(model_name, cleaned_sql, "agentic")

    def _standardize_table_sync_configuration(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Converts different table_sync_config formats into a single, consistent format."""
        if "tables" in config:
            return config["tables"]
            
        normalized_list = []
        for table_name, columns_list in config.items():
            if isinstance(columns_list, list):
                column_names = [column["column"] if isinstance(column, dict) else column for column in columns_list]
                normalized_list.append({
                    "table_name": table_name,
                    "schema_name": DEFAULT_SCHEMA,
                    "columns": ",".join(column_names)
                })
        return normalized_list

    def _build_staging_model_select_clause(self, framework_handler: TransformationFrameworkHandler, table_configuration: Dict[str, Any], column_transformations_config: Dict[str, Any]) -> str:
        """Builds the SELECT block for a staging model."""
        schema = table_configuration['schema_name']
        table = table_configuration['table_name']
        columns = [column.strip() for column in table_configuration.get('columns', '').split(',') if column.strip()]
        
        if not columns:
            return f"SELECT * FROM {framework_handler.format_source_table_reference(table, schema)}"

        table_transformations = column_transformations_config.get("tables", {}).get(table, {})
        select_lines = []
        for column_name in columns:
            action = table_transformations.get(column_name, "None")
            operation_type, _, aggregation_function = action.partition(":")
            select_lines.append(f"  {{{{ handle_column_transformation('{column_name}', '{schema}', '{table}', '{operation_type}', '{aggregation_function}') }}}} AS {column_name}")

        select_clause = "SELECT\n" + ",\n".join(select_lines)
        from_clause = f"FROM {framework_handler.format_source_table_reference(table, schema)}"
        return f"{select_clause}\n{from_clause}"

    def _build_join_transformation_sql(self, framework_handler: TransformationFrameworkHandler, join_config: Dict[str, Any]) -> str:
        """Builds the SQL for a join transformation."""
        primary_table = join_config.get("primary_table")
        target_tables = join_config.get("target_tables", [])
        if not primary_table or not target_tables:
            return ""

        all_columns, used_column_names = [], set()

        primary_columns_config = join_config.get("primary_table_columns", [])
        if primary_columns_config:
            print(f"Using configured columns for primary table {primary_table}: {primary_columns_config}")
            for i, column_name in enumerate(primary_columns_config):
                comma = "," if i > 0 else ""
                all_columns.append(f"  {comma}{primary_table}.{column_name}")
                used_column_names.add(column_name)

        from_clause = f"FROM {framework_handler.format_model_reference(f'stg_{framework_handler.schema}__{primary_table}')} AS {primary_table}"
        
        for target_config in target_tables:
            target_table = target_config.get("target_table")
            if not target_table: continue
            
            target_columns_config = target_config.get("columns", [])
            if target_columns_config:
                print(f"Using configured columns for target table {target_table}: {target_columns_config}")
                for column_name in target_columns_config:
                    if column_name != 'id':
                        alias = f" AS {target_table}_{column_name}" if column_name in used_column_names else ""
                        all_columns.append(f"  ,{target_table}.{column_name}{alias}")
                        if not alias: used_column_names.add(column_name)         
            join_type = target_config.get("join_type", DEFAULT_JOIN_TYPE).upper()
            conditions = " AND ".join(
                f"{primary_table}.{join_condition.get('source_column')} = {target_table}.{join_condition.get('target_column')}"
                for join_condition in target_config.get("join_conditions", []) if join_condition.get('source_column') and join_condition.get('target_column')
            )
            if conditions:
                from_clause += f"\n  {join_type} JOIN {framework_handler.format_model_reference(f'stg_{framework_handler.schema}__{target_table}')} AS {target_table} ON {conditions}"
        
        if not all_columns:
            print("No columns selected, using fallback SELECT * for all tables")
            all_columns = [f"  {primary_table}.*"]
            for target_config in target_tables:
                target_table = target_config.get("target_table")
                if target_table:
                    all_columns.append(f"  ,{target_table}.*")
        
        print(f"Final column selection: {[column.strip() for column in all_columns]}")
        select_clause = "SELECT\n" + "\n".join(all_columns)
        return f"{select_clause}\n{from_clause}"

    def _sanitize_agentic_sql(self, sql_code: str, framework: str) -> str:
        """Cleans and validates SQL from an agentic source."""
        sql_code = re.sub(r'^```sql\n|```$', '', sql_code, flags=re.MULTILINE).strip()
        
        if framework.lower() == "sqlmesh":
            if not sql_code.strip().endswith(';'):
                sql_code += ';'
        else:
            sql_code = sql_code.rstrip(';')
        return sql_code

    def _create_model_name_from_transformation_intent(self, intent: str, transformation_index: int) -> str:
        """Generates a sanitized model name from an intent string."""
        if not intent:
            return f"agentic_transformation_{transformation_index + 1}"
        
        words = re.findall(r'\b\w{MIN_WORD_LENGTH,}\b', intent.lower())
        key_words = [word for word in words if word not in ['that', 'this', 'with', 'from', 'into']]
        base_name = "_".join(key_words[:MAX_KEYWORDS]) or f"agentic_transformation_{transformation_index + 1}"
        
        model_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        return f"transformation_{model_name}" if not model_name[0].isalpha() else model_name

    def _generate_dbt_sources(self, framework_handler: DBTHandler, table_sync_details: List[Dict[str, Any]]):
        """Generates a sources.yml file for dbt."""
        source_yaml_tables = []
        for table_configuration in table_sync_details:
            table_name = table_configuration['table_name']
            columns_str = table_configuration.get('columns', '')
            if not columns_str: continue

            columns = [{"name": column.strip(), "description": f"The {column.strip()} field."} for column in columns_str.split(',')]
            source_yaml_tables.append({
                "name": table_name,
                "description": f"Raw {table_name} data from {framework_handler.schema} schema.",
                "columns": columns
            })

        if source_yaml_tables:
            sources_dict = {
                "version": 2,
                "sources": [{
                    "name": "raw_data",
                    "schema": framework_handler.schema,
                    "description": "Source definitions for raw data tables.",
                    "tables": source_yaml_tables
                }]
            }
            yaml_content = yaml.dump(sources_dict, indent=2, sort_keys=False)
            escaped_yaml = yaml_content.replace("'", "'\"'\"'")
            framework_handler.runner.docker_manager.exec_command(
               command=["sh", "-c", f"echo '{escaped_yaml}' > {framework_handler.workdir}/transform/models/sources/sources.yml"],
               workdir=framework_handler.workdir
            ) 