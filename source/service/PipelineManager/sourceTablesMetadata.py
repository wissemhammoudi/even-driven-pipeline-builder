from abc import ABC, abstractmethod
import psycopg2
from typing import Dict, List, Any


class SourceTableMetadata(ABC):
    
    def __init__(self, **connection_params):

        self.connection_params = connection_params
    
    @abstractmethod
    def _get_connection(self):
        pass
    
    @abstractmethod
    def get_schema_info(self, schema: str) -> Dict[str, Any]:
        pass


class PostgreSQLSourceMetadata(SourceTableMetadata):
    
    def __init__(self, host: str, dbname: str, user: str, password: str, port: int = 5432):
        super().__init__(host=host, dbname=dbname, user=user, password=password, port=port)
    
    def _get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def get_schema_info(self, schema: str) -> Dict[str, Any]:
        connection = self._get_connection()
        cursor = connection.cursor()
        
        db_structure = {}
        
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """, (schema,))
        tables = cursor.fetchall()
        
        db_structure[schema] = {}
        
        for (table,) in tables:
            cursor.execute("""
                SELECT 
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.character_maximum_length,
                    CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_schema = %s
                        AND tc.table_name = %s
                ) pk ON c.column_name = pk.column_name
                WHERE c.table_schema = %s AND c.table_name = %s
                ORDER BY c.ordinal_position;
            """, (schema, table, schema, table))
            columns = cursor.fetchall()
            
            db_structure[schema][table] = [{
                "column_name": col[0],
                "data_type": col[1],
                "is_nullable": col[2],
                "character_maximum_length": col[3],
                "is_primary_key": col[4]
            } for col in columns]
        
        cursor.close()
        connection.close()
        return db_structure
    

def create_source_metadata(source_type: str, **connection_params) -> SourceTableMetadata:

    source_type = source_type.lower()
    
    if source_type == 'postgresql':
        return PostgreSQLSourceMetadata(**connection_params)
    else:
        supported_types = ['postgresql']
        raise ValueError(f"Unsupported source type: '{source_type}'. Supported types: {supported_types}")


