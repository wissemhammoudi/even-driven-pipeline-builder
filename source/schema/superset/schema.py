from pydantic import BaseModel

class VisualizationControl(BaseModel):
    pipeline_id: int
    user_id: int