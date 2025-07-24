from typing import Dict, Any, List
from source.service.PipelineManager.sourceTablesMetadata import create_source_metadata


def get_table_columns(table_name: str, schema: str, database_connection_params: Dict[str, Any]) -> List[str]:

    if not database_connection_params:
        print(f"Warning: No database connection parameters provided for table {table_name}")
        return []
    
    safe_connection_params = {k: v for k, v in database_connection_params.items() if k != "password"}
    print(f"Attempting to connect to database with params: {safe_connection_params}")
    
    try:
        source_metadata = create_source_metadata("postgresql", **database_connection_params)
        schema_info = source_metadata.get_schema_info(schema)
        
        if schema in schema_info and table_name in schema_info[schema]:
            columns = [column["column_name"] for column in schema_info[schema][table_name]]
            if columns:
                print(f"Successfully retrieved {len(columns)} columns for table {table_name}: {columns}")
                return columns
            else:
                print(f"No columns found for table {table_name}")
                return []
        else:
            print(f"Table {schema}.{table_name} not found in schema info")
            print(f"Available schemas: {list(schema_info.keys())}")
            if schema in schema_info:
                print(f"Available tables in {schema}: {list(schema_info[schema].keys())}")
            return []
    except Exception as e:
        print(f"Error getting columns for table {table_name}: {e}")
        print(f"Connection parameters used: {safe_connection_params}")
        return [] 