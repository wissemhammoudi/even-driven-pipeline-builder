from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from source.schema.pipeline_step.schema import StepBase,PipelineStepCreate
from enum import Enum


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: str
    step_list:List[StepBase]

class PipelineDelete(BaseModel):
    pipeline_id: int

class PipelineUpdate(BaseModel):
    pipeline_id: int
    name: Optional[str] = None
    description: Optional[str] = None

class StepAdd(BaseModel):
    pipeline_id: int
    step: PipelineStepCreate
class StepDelete(BaseModel):
    pipeline_id: int
    step_id: int 

class PipelineResponse(BaseModel):
    pipeline_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    is_deprecated: bool
    created_by: str  
    
    class Config:
        from_attributes = True

    
class ToolEnum(str, Enum):
    MELTANO = "meltano"
    DLT ="dlt"
    SQLMESH ="sqlmesh"
    DBT="dbt"
    SUPERSET="superset"
class DatabaseConfigurationEnum(str, Enum):
    database="database"
    dbname="dbname"
class StepTypeEnum(str, Enum):
    DATA_INGESTION = "data ingestion"
    DATA_TRANSFORMATION="data transformation"
    DATA_VISUALIZATION="data visualization"


class PluginTypeEnum(str, Enum):
    EXTRACTOR = "extractor"
    LOADER = "loader"
    UTILITY = "utility"
class PostgreSQLMetadataRequest(BaseModel):
    host: str
    dbname: str
    user: str
    password: str
    port: Optional[int] = 5432
    schema: str