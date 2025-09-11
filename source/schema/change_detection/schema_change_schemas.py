from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SchemaChangeResponse(BaseModel):
    """Response model for schema change detection"""
    table_name: str
    schema_name: str
    change_type: str
    change_details: Dict[str, Any]
    event_id: str
    source_connector: str
    timestamp: str


class DebeziumConnectorResponse(BaseModel):
    """Response model for Debezium connector operations"""
    success: bool
    message: str
    connector_info: Dict[str, Any]


class SchemaSummaryResponse(BaseModel):
    """Response model for schema summary"""
    schema_name: str
    tables: List[Dict[str, Any]]
    total_tables: int
    last_updated: Optional[str] = None


class SchemaChangeHistoryResponse(BaseModel):
    """Response model for schema change history"""
    table_name: str
    schema_name: str
    changes: List[Dict[str, Any]]
    total_changes: int


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str
    debezium: Dict[str, Any]
    kafka: Dict[str, Any]
    timestamp: str


class PostgreSQLMetadataRequest(BaseModel):
    """Request model for PostgreSQL metadata operations"""
    host: str
    port: int
    database: str
    username: str
    password: str
    schema_name: str  # Changed from 'schema' to 'schema_name' to avoid shadowing BaseModel.schema


class SchemaChangeEventRequest(BaseModel):
    """Request model for schema change events"""
    table_name: str
    schema_name: str
    change_type: str
    change_details: Dict[str, Any]
    source_connector: str


class KafkaTopicRequest(BaseModel):
    """Request model for Kafka topic operations"""
    topic_name: str
    partitions: int = 1
    replication_factor: int = 1


class ConnectorConfigRequest(BaseModel):
    """Request model for Debezium connector configuration"""
    connector_name: str
    database_hostname: str
    database_port: int
    database_user: str
    database_password: str
    database_dbname: str
    database_server_name: str
    table_include_list: Optional[str] = None
    schema_include_list: Optional[str] = None
