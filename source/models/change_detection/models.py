from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SqlEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from source.models.pipeline.models import Pipeline
from source.repository.database import Base
from source.schema.change_detection.schema import SchemaChangeTypeEnum

class SchemaChangeEvent(Base):
    __tablename__ = "schema_change"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.pipeline_id'), nullable=False)
    event_time = Column(DateTime, default=datetime.now, nullable=False)
    change_type = Column(SqlEnum(SchemaChangeTypeEnum), nullable=False)
    payload = Column(Text, nullable=False)
    pipeline = relationship("Pipeline", backref="schema_change") 