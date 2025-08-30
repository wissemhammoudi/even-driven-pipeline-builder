from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class SchemaChangeResponse(BaseModel):
    """Response model for schema change events"""
    table_name: str
    schema_name: str
    change_type: str
    change_details: Optional[Dict[str, Any]] = None
    event_id: str
    source_connector: str
    timestamp: str

class DebeziumConnectorResponse(BaseModel):
    """Response model for Debezium connector operations"""
    success: bool
    message: str
    connector_info: Optional[Dict[str, Any]] = None

class SchemaSummaryResponse(BaseModel):
    """Response model for schema summary"""
    schema_name: str
    total_tables: int
    total_columns: int
    total_indexes: int
    last_updated: str
    tables: List[Dict[str, Any]]

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

class DebeziumConnectorConfig(BaseModel):
    """Configuration model for Debezium connectors"""
    name: str
    config: Dict[str, Any]

class SchemaChangeEventRequest(BaseModel):
    """Request model for schema change events"""
    table_name: str
    schema_name: str = "public"
    change_type: str
    change_details: Optional[Dict[str, Any]] = None
    sql_statement: Optional[str] = None

class EventHandlerConfig(BaseModel):
    """Configuration model for event handlers"""
    handler_type: str
    handler_config: Dict[str, Any]
    enabled: bool = True
    priority: int = 1

class KafkaTopicConfig(BaseModel):
    """Configuration model for Kafka topics"""
    topic_name: str
    partitions: int = 1
    replication_factor: int = 1
    retention_ms: Optional[int] = None

class SchemaChangeNotificationConfig(BaseModel):
    """Configuration model for schema change notifications"""
    enabled: bool = True
    notification_channels: List[str] = ["kafka", "email", "slack"]
    notification_topic: str = "schema-change-notifications"
    email_recipients: Optional[List[str]] = None
    slack_webhook: Optional[str] = None

class AutomatedResponseConfig(BaseModel):
    """Configuration model for automated responses"""
    enabled: bool = True
    response_rules: List[Dict[str, Any]] = []
    backup_enabled: bool = False
    backup_retention_days: int = 30
    validation_enabled: bool = True
    downstream_notification_enabled: bool = True

class SchemaChangePolicy(BaseModel):
    """Policy model for schema changes"""
    table_name: str
    schema_name: str = "public"
    allowed_operations: List[str] = ["CREATE", "ALTER", "DROP"]
    requires_approval: bool = False
    approval_roles: List[str] = []
    notification_required: bool = True
    backup_required: bool = False
    validation_required: bool = True

class SchemaChangeAudit(BaseModel):
    """Audit model for schema changes"""
    event_id: str
    table_name: str
    schema_name: str
    change_type: str
    change_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    approved_by: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    rollback_available: bool = False
    rollback_timestamp: Optional[datetime] = None

class SchemaChangeMetrics(BaseModel):
    """Metrics model for schema changes"""
    total_changes: int
    changes_by_type: Dict[str, int]
    changes_by_schema: Dict[str, int]
    changes_by_table: Dict[str, int]
    changes_by_user: Dict[str, int]
    changes_by_hour: Dict[str, int]
    average_processing_time_ms: float
    success_rate: float
    last_change_timestamp: Optional[datetime] = None

class SchemaChangeRollback(BaseModel):
    """Rollback model for schema changes"""
    event_id: str
    original_change: SchemaChangeEvent
    rollback_sql: str
    rollback_timestamp: datetime
    rollback_user: str
    rollback_reason: str
    rollback_successful: bool
    rollback_details: Optional[Dict[str, Any]] = None

class SchemaChangeValidation(BaseModel):
    """Validation model for schema changes"""
    event_id: str
    validation_rules: List[str]
    validation_results: Dict[str, bool]
    validation_messages: List[str]
    validation_timestamp: datetime
    validation_user: str
    validation_passed: bool
    blocking_issues: List[str] = []
    warnings: List[str] = []

class SchemaChangeImpact(BaseModel):
    """Impact analysis model for schema changes"""
    event_id: str
    affected_tables: List[str]
    affected_views: List[str]
    affected_functions: List[str]
    downstream_systems: List[str]
    data_migration_required: bool
    estimated_downtime_minutes: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    impact_summary: str
    mitigation_strategies: List[str] = []
