from pydantic import BaseModel
from typing import Optional

class TransformationRequest(BaseModel):
    transformation: str
    schema_name: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
