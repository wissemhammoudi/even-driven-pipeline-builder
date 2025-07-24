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
