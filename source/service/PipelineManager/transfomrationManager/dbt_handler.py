from .base_handler import TransformationFrameworkHandler


class DBTHandler(TransformationFrameworkHandler):
    """dbt-specific implementation."""
    def create_model_file_content(self, model_name: str, sql_content: str) -> str:
        config = "{{ config(materialized='table') }}"
        return f"{config}\n\n{sql_content}"
        
    def format_source_table_reference(self, table_name: str, schema_name: str) -> str:
        return f"{{{{ source('raw_data', '{table_name}') }}}}"
        
    def format_model_reference(self, model_name: str) -> str:
        return f"{{{{ ref('{model_name}') }}}}" 