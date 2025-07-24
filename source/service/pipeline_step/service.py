from sqlalchemy.orm import Session
from source.models.pipeline_step.models import Step
from source.schema.pipeline_step.schema import StepCreate, StepUpdate
from source.repository.pipeline_step.repository import StepRepository
from source.exceptions.exceptions import StepNotFoundError


class StepService:
    def __init__(self):
        self.step_repository = StepRepository()

    def create_step(self, data: StepCreate):
        step = Step(
            name=data.name,
            description=data.description,
            step_config=data.step_config,
            pipeline_id=data.pipeline_id,
            order=data.order
        )
        
        return self.step_repository.create_step(step)

    def update_step(self, data: StepUpdate):
        step = self.step_repository.get_step_by_id(data.step_id)
        if not step:
            raise StepNotFoundError("Step not found")
        if data.name:
            step.name = data.name
        if data.description is not None:
            step.description = data.description
        if data.step_config:
            step.step_config = data.step_config
        self.step_repository.commit(self.db)
        return {
            "message": "Step updated successfully",
            "step": {
                "step_id": step.step_id,
                "name": step.name,
                "description": step.description,
                "step_config": step.step_config,
                "pipeline_id": step.pipeline_id
            }
        }

    def delete_step(self, step_id: int):
        step = self.step_repository.get_step_by_id(step_id)
        if not step:
            raise StepNotFoundError("Step not found")
        self.step_repository.mark_step_deleted(step)
        return {"message": "Step soft-deleted successfully"}
    
    def get_piplines_ids(self, step_ids: list[int]):
        pipelineids=[]
        for step_id in step_ids:
            step = self.step_repository.get_step_by_id(step_id)
            if not step:
                raise StepNotFoundError("Step not found")
            pipeline_id=self.step_repository.get_pipeline_id_by_step_id(step_id)
            pipelineids.append(pipeline_id)
        return list(set(pipelineids))
    
    def mark_deprecated(self, step_ids: list[int]):
        for step_id in step_ids:
            step = self.step_repository.get_step_by_id(step_id)
            if step is None:
                raise ValueError(f"Step with ID {step_id} not found")

            self.step_repository.mark_deprecated(step)

    def get_steps_by_pipeline(self, pipeline_id: int):
        return self.step_repository.get_step_by_pipeline(pipeline_id)
    
    def get_steps_id_by_pipeline(self, pipeline_id: int):
        return self.step_repository.get_step_id_by_pipeline(pipeline_id)
    
    def get_pipeline_id_by_step_id(self, step_id: int):
        return self.step_repository.get_pipeline_id_by_step_id(step_id)
    
    def rollback(self):
        self.step_repository.rollback()
