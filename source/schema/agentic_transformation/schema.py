from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgenticTransformationCreate(BaseModel):
    transformation: str
    schema_name: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

class AgenticTransformationUpdate(BaseModel):
    transformation: Optional[str] = None
    schema_name: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None

class AgenticTransformationResponse(BaseModel):
    id: int
    transformation: str
    schema_name: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TransformationRequest(BaseModel):
    transformation: str
    schema_name: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
