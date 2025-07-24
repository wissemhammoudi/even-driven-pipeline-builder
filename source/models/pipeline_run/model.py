from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from source.repository.database import Base
from source.schema.pipeline_run.schema import RunStatus

class PipelineRun(Base):
    __tablename__ = "pipeline_run"

    run_id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.pipeline_id"))
    pipeline_run= Column(String(100), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Enum(RunStatus))
    created_by = Column(Integer, ForeignKey("users.user_id"))
    is_deleted = Column(Boolean, default=False)

    pipeline = relationship("Pipeline", back_populates="pipeline_runs")
    creator = relationship("User", back_populates="pipeline_runs")
