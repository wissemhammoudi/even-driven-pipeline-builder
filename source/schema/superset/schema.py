from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SupersetCreate(BaseModel):
    pipeline_id: int
    user_id: str 
    superset_config: Dict[str, Any]

class SupersetUpdate(BaseModel):
    superset_config: Optional[Dict[str, Any]] = None

class SupersetResponse(BaseModel):
    id: int
    pipeline_id: int
    user_id: str  
    superset_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VisualizationControl(BaseModel):
    pipeline_id: int
    user_id: str  