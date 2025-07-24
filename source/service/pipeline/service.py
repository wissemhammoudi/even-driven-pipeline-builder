from datetime import datetime
from typing import List
from source.models.pipeline.models import Pipeline
from source.schema.pipeline.schema import PipelineCreate, PipelineDelete, StepAdd, StepDelete, PipelineUpdate, PipelineResponse,PipelineStatusEnum
from source.repository.pipeline.repository import PipelineRepository
from source.service.pipeline_step.service import StepService
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.exceptions.exceptions import PipelineNotFoundError,StepIdNotFoundInPipeline
from source.schema.pipeline_step.schema import StepCreate
from source.schema.step_stepconfi_association.schema import StepConfigurationAssociationCreate
from source.service.PipelineManager.pipelineManager import PipelineManager
from source.service.dashboard_pipeline_association.service import DashboardPipelineAssociationService


class PipelineService:
    def __init__(self):
        self.pipeline_repository = PipelineRepository()
        self.step_service = StepService()
        self.StepConfigurationAssociation=StepConfigurationAssociationService()
        self.dashboard_pipeline_association=DashboardPipelineAssociationService()

    def list_pipelines(self, user_id: int, offset: int = 0, limit: int = 10, deprecated: bool = False, name: str = None, created_date=None):
        try:

            pipelines, total_count = self.pipeline_repository.get_paginated_pipelines(
                    offset=offset, 
                    limit=limit, 
                    deprecated=deprecated, 
                    name=name, 
                    created_date=created_date,
                    user_id=user_id  
                )   
            
            return {
                "data": [PipelineResponse.from_orm(pipeline) for pipeline in pipelines],
                "total": total_count,
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            print(f"Service error in list_pipelines: {str(e)}")
            raise
    
    def list_all_pipelines_ids(self) -> List[int]:
        return self.pipeline_repository.get_all_pipelines_ids()
    
    def get_pipline_by_id(self,pipeline_id:int) -> Pipeline:
        return self.pipeline_repository.get_pipline_by_id(pipeline_id)

    def list_pipelines_by_user(self, user_id: int) -> List[Pipeline]:
        pipelines = self.pipeline_repository.get_active_pipeline_by_user_id(user_id)
        return pipelines
    def create_pipeline(self, pipeline_data: PipelineCreate):
        if not pipeline_data.name or not pipeline_data.step_list:
            return {"error": "Pipeline name and at least one step are required"}, 400

        for step in pipeline_data.step_list:
            if not step.step_config.get("tool"):
                return {"error": f"Step {step.name} is missing tool configuration"}, 400
            if not step.step_config.get("config_ids"):
                return {"error": f"Step {step.name} is missing config_ids"}, 400

        pipeline = Pipeline(
                name=pipeline_data.name,
                description=pipeline_data.description,
                created_by=pipeline_data.created_by,
                created_at=datetime.utcnow(),
                status=PipelineStatusEnum.stopped,
            )
        pipeline_id = self.pipeline_repository.create_Pipeline(pipeline)
        Pipeline_init = PipelineManager()
        i=1
        error_message = None
        
        try:
            for step_data in pipeline_data.step_list: 
                step = StepCreate(
                        name=step_data.name,
                        description=step_data.description,
                        step_config=step_data.step_config,
                        config_ids=step_data.config_ids,  
                        pipeline_id=pipeline_id,
                        order=i
                    )  
                i+=1    
                step = self.step_service.create_step(step)
                step_id = step.step_id
                
                for config_id in step_data.config_ids:
                    config_association = StepConfigurationAssociationCreate(
                            step_id=step_id,
                            step_config_id=config_id
                        )
                    self.StepConfigurationAssociation.add_association(config_association)
            
            for step_data in pipeline_data.step_list:
                github_repo_name = f"{pipeline_data.name}_{pipeline_id}_{step_data.order}"
                print(f"Processing step with repo: {github_repo_name}")
                runner = Pipeline_init.get_runner(str(step_data.step_config["tool"]))
                
                is_visual = step_data.step_config.get("config_type") == "data visualization"
                Pipeline_init.add_step(github_repo_name, runner, step_data, is_visual)
            
            dashboard_id=Pipeline_init.create_pipeline()
            self.dashboard_pipeline_association.create_association(pipeline_id, dashboard_id)
            return {"message": "Pipeline created successfully", "pipeline_id": pipeline_id}, 201
            
        except Exception as e:
            try:
                Pipeline_init.cleanup()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {str(cleanup_error)}")
            
            error_message = str(e) if not error_message else error_message
            return {
                "error": f"Failed to create pipeline: {error_message}",
                "pipeline_id": pipeline_id
            }, 500

    def delete_pipeline(self, pipeline_data: PipelineDelete):
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(pipeline_data.pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found or already deleted")
        steps_ids=self.step_service.get_steps_id_by_pipeline(pipeline_data.pipeline_id)
        for step_id in steps_ids:
            self.step_service.delete_step(step_id)
            self.StepConfigurationAssociation.delete_by_step_id(step_id)



        self.pipeline_repository.mark_pipeline_deleted(pipeline)

    def get_pipeline_steps(self, pipeline_id: int) -> List[int]:
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found")
        return pipeline.steps_id 

    def add_step_to_pipeline(self, step_data: StepAdd) -> dict:
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(step_data.pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found or is deleted")

        if pipeline.steps_id is None:
            pipeline.steps_id = []
        step_id_added=self.step_service.create_step(step_data.step)
        pipeline.steps_id.append(step_id_added)
        self.pipeline_repository.commit()
        return {"message": f"Added {step_id_added} step to the pipeline. Steps now: {pipeline.steps_id}"}
    def delete_steps_from_pipeline(self,step_data:StepDelete):
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(step_data.pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found or is deleted")

        if  step_data.step_id not in pipeline.steps_id:
            raise StepIdNotFoundInPipeline(f"Step ID {step_data.step_id} is not part of the pipeline {pipeline.steps_id}")

        pipeline.steps_id.remove(step_data.step_id)

        self.pipeline_repository.commit()
        self.step_service.delete_step(step_id=step_data.step_id)
        return {"message": f"Step ID {step_data.step_id} has been removed from pipeline {step_data.pipeline_id}"}
 

    def update_pipeline(self, pipeline_data: PipelineUpdate):
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(pipeline_data.pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found or is deleted")

        if pipeline_data.name is not None:
            pipeline.name = pipeline_data.name
        if pipeline_data.description is not None:
            pipeline.description = pipeline_data.description

        self.pipeline_repository.commit()
        return {"message": "Pipeline has been updated successfully"}
    def mark_deprecated(self,pipline_id:int,stepsids:list[int]):

        return self.pipeline_repository.mark_deprecated(pipline_id)
        
    def get_pipeline_steps_details(self, pipeline_id: int):
        pipeline = self.pipeline_repository.get_Active_Pipeline_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError("Pipeline not found")
        return self.step_service.get_steps_by_pipeline(pipeline_id)