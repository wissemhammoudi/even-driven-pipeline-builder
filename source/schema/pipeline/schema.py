from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from source.schema.pipeline_step.schema import StepBase,StepCreate
from enum import Enum


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    created_by: int
    step_list:List[StepBase]

class PipelineDelete(BaseModel):
    pipeline_id: int

class PipelineUpdate(BaseModel):
    pipeline_id: int
    name: Optional[str] = None
    description: Optional[str] = None

class StepAdd(BaseModel):
    pipeline_id: int
    step: StepCreate
class StepDelete(BaseModel):
    pipeline_id: int
    step_id: int 

class ToolEnum(str, Enum):
    MELTANO = "meltano"
    DLT ="dlt"
    SQLMESH ="sqlmesh"
    DBT="dbt"
    SUPERSET="superset"

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
class PipelineStatusEnum(Enum):
    running = "running"
    stopped = "stopped"
    broken = "broken"

class PipelineResponse(BaseModel):
    pipeline_id: int
    name: str
    description: Optional[str] = None
    created_by: int
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    step_list: List[StepBase] = []