from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

Base = declarative_base()

class SchemaChange(Base):
    __tablename__ = "schema_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False, index=True)
    schema_name = Column(String(255), nullable=False, default="public")
    change_type = Column(String(50), nullable=False)  # CREATE, ALTER, DROP, RENAME
    change_details = Column(JSON, nullable=True)
    sql_statement = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    event_id = Column(String(255), nullable=True, index=True)
    source_connector = Column(String(255), nullable=True)

class SchemaChangeEvent(BaseModel):
    table_name: str
    schema_name: str = "public"
    change_type: str
    change_details: Optional[Dict[str, Any]] = None
    sql_statement: Optional[str] = None
    event_id: Optional[str] = None
    source_connector: Optional[str] = None
    timestamp: datetime = datetime.now()

class DebeziumChangeEvent(BaseModel):
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    source: Dict[str, Any]
    op: str  # c=create, u=update, d=delete, r=read
    ts_ms: int
    transaction: Optional[Dict[str, Any]] = None

class SchemaChangeNotification(BaseModel):
    event_type: str = "schema_change"
    table_name: str
    schema_name: str
    change_type: str
    change_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    event_id: str
