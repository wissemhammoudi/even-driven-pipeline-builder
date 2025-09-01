from abc import ABC, abstractmethod
import psycopg2
from typing import Dict, Any
import logging
from datetime import datetime


class SourceTableMetadata(ABC):
    
    def __init__(self, **connection_params):
        self.connection_params = connection_params
        self.last_connection_test = None
        self.connection_status = "unknown"
    
    @abstractmethod
    def _get_connection(self):
        pass
    
    @abstractmethod
    def get_schema_info(self, schema: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test the database connection and return status information"""
        pass

class PostgreSQLSourceMetadata(SourceTableMetadata):
    
    def __init__(self, host: str, dbname: str, user: str, password: str, port: int = 5432):
        super().__init__(host=host, dbname=dbname, user=user, password=password, port=port)
    
    def _get_connection(self):
        """Get a database connection with error handling"""
        try:
            connection = psycopg2.connect(**self.connection_params)
            return connection
        except psycopg2.Error as e:
            raise ConnectionError(f"PostgreSQL connection failed: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the PostgreSQL connection and return detailed status information"""
        start_time = datetime.now()
        connection = None
        cursor = None
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT version()")
            version_info = cursor.fetchone()
            
            # Test schema access
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name
                LIMIT 5
            """)
            available_schemas = [row[0] for row in cursor.fetchall()]
                        
            cursor.execute("SHOW shared_preload_libraries")
            shared_libraries = cursor.fetchone()[0]
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000 
            
            self.connection_status = "connected"
            self.last_connection_test = end_time.isoformat()
            
            return {
                "status": "success",
                "connection_status": "connected",
                "response_time_ms": round(response_time, 2),
                "database_info": {
                    "version": version_info[0] if version_info else "unknown",
                    "shared_libraries": shared_libraries
                },
                "schema_info": {
                    "available_schemas": available_schemas,
                },
                "connection_params": {
                    "host": self.connection_params.get('host'),
                    "port": self.connection_params.get('port'),
                    "database": self.connection_params.get('dbname'),
                    "user": self.connection_params.get('user')
                },
                "timestamp": end_time.isoformat()
            }
            
        except psycopg2.OperationalError as e:
            error_msg = f"Operational error: {str(e)}"
            self.connection_status = "connection_failed"
            self.last_connection_test = datetime.now().isoformat()
            
            return {
                "status": "error",  
                "connection_status": "connection_failed",
                "error_type": "operational_error",
                "error_message": str(e),
                "error_code": getattr(e, 'pgerror', None),
                "timestamp": datetime.now().isoformat()
            }
            
        except psycopg2.Error as e:
            error_msg = f"PostgreSQL error: {str(e)}"
            self.connection_status = "error"
            self.last_connection_test = datetime.now().isoformat()
            
            return {
                "status": "error",
                "connection_status": "error",
                "error_type": "postgresql_error",
                "error_message": str(e),
                "error_code": getattr(e, 'pgerror', None),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.connection_status = "error"
            self.last_connection_test = datetime.now().isoformat()
            
            return {
                "status": "error",
                "connection_status": "error",
                "error_type": "unexpected_error",
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_schema_info(self, schema: str) -> Dict[str, Any]:
        """Get schema information with improved error handling"""
        connection = None
        cursor = None
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            
            db_structure = {}
            
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = %s
            """, (schema,))
            
            if not cursor.fetchone():
                raise ValueError(f"Schema '{schema}' does not exist")
            
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
            
            return db_structure
            
        except Exception as e:
            raise
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    

def create_source_metadata(source_type: str, **connection_params) -> SourceTableMetadata:
    """Factory function to create source metadata objects"""
    source_type = source_type.lower()
    
    if source_type == 'postgresql':
        return PostgreSQLSourceMetadata(**connection_params)
    else:
        supported_types = ['postgresql']
        raise ValueError(f"Unsupported source type: '{source_type}'. Supported types: {supported_types}")

