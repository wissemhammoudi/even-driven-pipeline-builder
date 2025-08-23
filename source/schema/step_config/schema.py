from pydantic import BaseModel
from typing import Optional, Dict

class Step_Config(BaseModel):
    step_config_id: int
    type: str
    tool: str
    plugin_type: str
    plugin_name: str
    is_deprecated: bool
    config: Optional[Dict] = None

class deprecation_data(BaseModel):
    step_config_id:int

class StepConfigCreate(BaseModel):
    type: str
    tool: str
    plugin_type: str
    plugin_name: str
    config: Optional[Dict] = None

class StepConfigUpdate(BaseModel):
    type: Optional[str] = None
    tool: Optional[str] = None
    plugin_type: Optional[str] = None
    plugin_name: Optional[str] = None
    config: Optional[Dict] = None
    is_deprecated: Optional[bool] = None

class StepConfigResponse(BaseModel):
    step_config_id: int
    type: str
    tool: str
    plugin_type: str
    plugin_name: str
    is_deprecated: bool
    config: Optional[Dict] = None

    class Config:
        from_attributes = True
