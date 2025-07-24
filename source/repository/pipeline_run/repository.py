from source.models.pipeline_run.model import PipelineRun
from source.repository.database import get_db

database= get_db()

class PipelineRunRepository:
    def __init__(self):
        self.db = database

    def create(self, run: PipelineRun) -> PipelineRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run
    
    def get_pipeline_run_by_pipeline_id(self,pipeline_id:int):
        return self.db.query(PipelineRun).filter(PipelineRun.pipeline_id == pipeline_id).order_by(PipelineRun.start_time.desc()).all()
    
    def get_pipeline_run_by_run_id(self,run_id:int):
        return self.db.query(PipelineRun).filter(PipelineRun.run_id == run_id).first()
    
    def commit(self):
        self.db.commit()
    
    def update(self, run: PipelineRun) -> PipelineRun:
        self.db.commit()
        self.db.refresh(run)
        return run