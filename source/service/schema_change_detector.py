import logging
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from source.config.config import database_config, debezium_config
from source.models.schema_change import SchemaChangeEvent, DebeziumChangeEvent, SchemaChangeNotification
import uuid

logger = logging.getLogger(__name__)

class SchemaChangeDetector:
    def __init__(self):
        self.engine = create_engine(database_config.SQLALCHEMY_DATABASE_URI)
        self.inspector = inspect(self.engine)
        self.schema_cache = {}
        self.last_check = None
        
    def get_current_schema(self, schema_name: str = "public") -> Dict[str, Any]:
        """Get the current database schema"""
        try:
            schema_info = {
                "tables": {},
                "last_updated": datetime.now().isoformat()
            }
            
            # Get all tables in the schema
            tables = self.inspector.get_table_names(schema=schema_name)
            
            for table_name in tables:
                table_info = {
                    "columns": {},
                    "indexes": [],
                    "constraints": []
                }
                
                # Get column information
                columns = self.inspector.get_columns(table_name, schema=schema_name)
                for column in columns:
                    table_info["columns"][column["name"]] = {
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "default": column["default"],
                        "primary_key": column.get("primary_key", False)
                    }
                
                # Get index information
                indexes = self.inspector.get_indexes(table_name, schema=schema_name)
                table_info["indexes"] = indexes
                
                # Get constraint information
                constraints = self.inspector.get_unique_constraints(table_name, schema=schema_name)
                table_info["constraints"] = constraints
                
                schema_info["tables"][table_name] = table_info
            
            return schema_info
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting current schema: {str(e)}")
            return {}
    
    def detect_schema_changes(self, schema_name: str = "public") -> List[SchemaChangeEvent]:
        """Detect schema changes by comparing current schema with cached schema"""
        current_schema = self.get_current_schema(schema_name)
        cached_schema = self.schema_cache.get(schema_name, {})
        
        changes = []
        
        if not cached_schema:
            # First time running, cache the current schema
            self.schema_cache[schema_name] = current_schema
            logger.info(f"Initial schema cached for schema '{schema_name}'")
            return changes
        
        # Compare tables
        current_tables = set(current_schema.get("tables", {}).keys())
        cached_tables = set(cached_schema.get("tables", {}).keys())
        
        # New tables
        new_tables = current_tables - cached_tables
        for table_name in new_tables:
            changes.append(SchemaChangeEvent(
                table_name=table_name,
                schema_name=schema_name,
                change_type="CREATE",
                change_details={"operation": "table_created"},
                event_id=str(uuid.uuid4()),
                source_connector="schema_detector"
            ))
        
        # Dropped tables
        dropped_tables = cached_tables - current_tables
        for table_name in dropped_tables:
            changes.append(SchemaChangeEvent(
                table_name=table_name,
                schema_name=schema_name,
                change_type="DROP",
                change_details={"operation": "table_dropped"},
                event_id=str(uuid.uuid4()),
                source_connector="schema_detector"
            ))
        
        # Check for table modifications
        common_tables = current_tables & cached_tables
        for table_name in common_tables:
            current_table = current_schema["tables"][table_name]
            cached_table = cached_schema["tables"][table_name]
            
            # Check column changes
            column_changes = self._detect_column_changes(
                table_name, schema_name, current_table, cached_table
            )
            changes.extend(column_changes)
            
            # Check index changes
            index_changes = self._detect_index_changes(
                table_name, schema_name, current_table, cached_table
            )
            changes.extend(index_changes)
        
        # Update cache if there are changes
        if changes:
            self.schema_cache[schema_name] = current_schema
            logger.info(f"Schema changes detected: {len(changes)} changes")
        
        return changes
    
    def _detect_column_changes(self, table_name: str, schema_name: str, 
                              current_table: Dict, cached_table: Dict) -> List[SchemaChangeEvent]:
        """Detect column-level changes in a table"""
        changes = []
        current_columns = current_table.get("columns", {})
        cached_columns = cached_table.get("columns", {})
        
        # New columns
        new_columns = set(current_columns.keys()) - set(cached_columns.keys())
        for column_name in new_columns:
            changes.append(SchemaChangeEvent(
                table_name=table_name,
                schema_name=schema_name,
                change_type="ALTER",
                change_details={
                    "operation": "column_added",
                    "column_name": column_name,
                    "column_info": current_columns[column_name]
                },
                event_id=str(uuid.uuid4()),
                source_connector="schema_detector"
            ))
        
        # Dropped columns
        dropped_columns = set(cached_columns.keys()) - set(current_columns.keys())
        for column_name in dropped_columns:
            changes.append(SchemaChangeEvent(
                table_name=table_name,
                schema_name=schema_name,
                change_type="ALTER",
                change_details={
                    "operation": "column_dropped",
                    "column_name": column_name
                },
                event_id=str(uuid.uuid4()),
                source_connector="schema_detector"
            ))
        
        # Modified columns
        common_columns = set(current_columns.keys()) & set(cached_columns.keys())
        for column_name in common_columns:
            current_col = current_columns[column_name]
            cached_col = cached_columns[column_name]
            
            if current_col != cached_col:
                changes.append(SchemaChangeEvent(
                    table_name=table_name,
                    schema_name=schema_name,
                    change_type="ALTER",
                    change_details={
                        "operation": "column_modified",
                        "column_name": column_name,
                        "old_value": cached_col,
                        "new_value": current_col
                    },
                    event_id=str(uuid.uuid4()),
                    source_connector="schema_detector"
                ))
        
        return changes
    
    def _detect_index_changes(self, table_name: str, schema_name: str,
                             current_table: Dict, cached_table: Dict) -> List[SchemaChangeEvent]:
        """Detect index-level changes in a table"""
        changes = []
        current_indexes = current_table.get("indexes", [])
        cached_indexes = cached_table.get("indexes", [])
        
        # Simple comparison - in production you might want more sophisticated index comparison
        if current_indexes != cached_indexes:
            changes.append(SchemaChangeEvent(
                table_name=table_name,
                schema_name=schema_name,
                change_type="ALTER",
                change_details={
                    "operation": "indexes_changed",
                    "old_indexes": cached_indexes,
                    "new_indexes": current_indexes
                },
                event_id=str(uuid.uuid4()),
                source_connector="schema_detector"
            ))
        
        return changes
    
    def process_debezium_event(self, event_data: Dict[str, Any]) -> Optional[SchemaChangeEvent]:
        """Process a Debezium change event and extract schema change information"""
        try:
            # Parse the Debezium event
            debezium_event = DebeziumChangeEvent(**event_data)
            
            # Extract table information from source
            source = debezium_event.source
            table_name = source.get("table", "")
            schema_name = source.get("schema", "public")
            
            # Check if this is a schema change event
            if self._is_schema_change_event(debezium_event):
                change_type = self._determine_change_type(debezium_event)
                
                return SchemaChangeEvent(
                    table_name=table_name,
                    schema_name=schema_name,
                    change_type=change_type,
                    change_details={
                        "debezium_operation": debezium_event.op,
                        "timestamp_ms": debezium_event.ts_ms,
                        "source": source
                    },
                    event_id=str(uuid.uuid4()),
                    source_connector="debezium"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing Debezium event: {str(e)}")
            return None
    
    def _is_schema_change_event(self, event: DebeziumChangeEvent) -> bool:
        """Determine if a Debezium event represents a schema change"""
        # This is a simplified check - in production you might want more sophisticated logic
        # to detect actual schema changes vs data changes
        
        # Check if the event has schema change indicators
        if hasattr(event, 'source') and event.source:
            # Look for schema change indicators in the source metadata
            source = event.source
            if 'schema' in source and 'table' in source:
                # This could be enhanced with more specific schema change detection logic
                return True
        
        return False
    
    def _determine_change_type(self, event: DebeziumChangeEvent) -> str:
        """Determine the type of schema change from a Debezium event"""
        # This is a simplified mapping - in production you might want more sophisticated logic
        
        if event.op == 'c':  # Create
            return "CREATE"
        elif event.op == 'u':  # Update
            return "ALTER"
        elif event.op == 'd':  # Delete
            return "DROP"
        else:
            return "ALTER"  # Default to ALTER for unknown operations
    
    def get_schema_history(self, table_name: str, schema_name: str = "public", 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get schema change history for a specific table"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT * FROM schema_changes 
                    WHERE table_name = :table_name AND schema_name = :schema_name
                    ORDER BY detected_at DESC 
                    LIMIT :limit
                """)
                
                result = conn.execute(query, {
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "limit": limit
                })
                
                return [dict(row._mapping) for row in result]
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting schema history: {str(e)}")
            return []
    
    def clear_schema_cache(self, schema_name: str = "public"):
        """Clear the schema cache for a specific schema"""
        if schema_name in self.schema_cache:
            del self.schema_cache[schema_name]
            logger.info(f"Schema cache cleared for schema '{schema_name}'")
    
    def get_schema_summary(self, schema_name: str = "public") -> Dict[str, Any]:
        """Get a summary of the current schema"""
        try:
            schema_info = self.get_current_schema(schema_name)
            
            summary = {
                "schema_name": schema_name,
                "total_tables": len(schema_info.get("tables", {})),
                "total_columns": 0,
                "total_indexes": 0,
                "last_updated": schema_info.get("last_updated"),
                "tables": []
            }
            
            for table_name, table_info in schema_info.get("tables", {}).items():
                table_summary = {
                    "name": table_name,
                    "columns": len(table_info.get("columns", {})),
                    "indexes": len(table_info.get("indexes", [])),
                    "constraints": len(table_info.get("constraints", []))
                }
                summary["tables"].append(table_summary)
                summary["total_columns"] += table_summary["columns"]
                summary["total_indexes"] += table_summary["indexes"]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting schema summary: {str(e)}")
            return {}
