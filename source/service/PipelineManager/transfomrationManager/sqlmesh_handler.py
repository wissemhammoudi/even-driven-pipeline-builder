from .base_handler import TransformationFrameworkHandler


class SQLMeshHandler(TransformationFrameworkHandler):
    """SQLMesh-specific implementation."""
    def create_model_file_content(self, model_name: str, sql_content: str) -> str:
        model_fqn = f"{self.schema}.{model_name}"
        header = f"MODEL (\n  name {model_fqn},\n  dialect postgres,\n  kind FULL\n);"
        return f"{header}\n\nJINJA_QUERY_BEGIN;\n{sql_content}\nJINJA_END;"
        
    def format_source_table_reference(self, table_name: str, schema_name: str) -> str:
        return f"{schema_name}.{table_name}"
        
    def format_model_reference(self, model_name: str) -> str:
        return f"{self.schema}.{model_name}" 