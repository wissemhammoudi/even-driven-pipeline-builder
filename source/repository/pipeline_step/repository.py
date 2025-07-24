from source.models.pipeline_step.models import Step
from source.repository.database import get_db

database= get_db()

class StepRepository:
    def __init__(self):
        self.db = database
    
    def create_step(self, step: Step):
        try:

            self.db.add(step)
            self.db.commit()
            self.db.refresh(step) 
            print(step)
            return step
        except Exception as e:
            self.db.rollback()
            raise e

    def get_step_by_pipeline(self, pipeline_id: int):
        return self.db.query(Step).filter(
            Step.pipeline_id == pipeline_id,
            Step.is_deleted == False,
        ).all()

    def get_step_by_id(self, step_id: int):
        return self.db.query(Step).filter(
            Step.step_id == step_id,
            Step.is_deleted == False,
        ).first()

    def mark_step_deleted(self, step: Step):
        try:
            step.is_deleted = True  
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def mark_deprecated(self, step: Step):
        try:
            step.is_deprecated= True  
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def get_step_id_by_pipeline(self, pipeline_id: int):
        step_ids = self.db.query(Step.step_id).filter(
            Step.pipeline_id == pipeline_id,
            Step.is_deleted == False,
        ).all()
        return [sid[0] for sid in step_ids]

    def get_pipeline_id_by_step_id(self, step_id: int):
        result = self.db.query(Step.pipeline_id).filter(
            Step.step_id == step_id,
            Step.is_deleted == False,
        ).first()
        return result[0] if result else None

    def commit(self):
        self.db.commit()
    def rollback(self):
        self.db.rollback()
