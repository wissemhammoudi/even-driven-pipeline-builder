import logging
from datetime import datetime
from typing import List
from source.models.pipeline.models import Pipeline
from source.schema.pipeline.schema import PipelineCreate, PipelineDelete, StepAdd, StepDelete, PipelineUpdate, PipelineResponse, StepTypeEnum
from source.repository.pipeline.repository import PipelineRepository
from source.service.pipeline_step.service import PipelineStepService
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.exceptions.exceptions import PipelineNotFoundError, StepIdNotFoundInPipeline
from source.schema.pipeline_step.schema import PipelineStepCreate
from source.schema.step_configuration_association.schema import StepConfigurationAssociationCreate
from source.service.PipelineManager.pipelineManager import PipelineManager
from source.service.dashboard_pipeline_association.service import DashboardPipelineAssociationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self):
        self.pipeline_repository = PipelineRepository()
        self.step_service = PipelineStepService()
        self.StepConfigurationAssociation=StepConfigurationAssociationService()
        self.dashboard_pipeline_association=DashboardPipelineAssociationService()

    def list_pipelines(self, user_id: str, offset: int = 0, limit: int = 10, deprecated: bool = False, name: str = None, created_date=None):
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

    def list_pipelines_by_user(self, user_id: str) -> List[Pipeline]:
        pipelines = self.pipeline_repository.get_active_pipeline_by_user_id(user_id)
        return pipelines
    def create_pipeline(self, pipeline_data: PipelineCreate):
        logger.info(f"🚀 Starting pipeline creation: {pipeline_data.name}")
        logger.info(f"👤 Created by: {pipeline_data.created_by}")
        logger.info(f"📝 Description: {pipeline_data.description}")
        logger.info(f"📋 Number of steps: {len(pipeline_data.step_list)}")
        
        if not pipeline_data.name or not pipeline_data.step_list:
            logger.error("❌ Pipeline name and at least one step are required")
            return {"error": "Pipeline name and at least one step are required"}, 400

        logger.info("🔍 Validating step configurations...")
        for step in pipeline_data.step_list:
            logger.info(f"🔧 Validating step: {step.name}")
            if not step.step_config.get("tool"):
                logger.error(f"❌ Step {step.name} is missing tool configuration")
                return {"error": f"Step {step.name} is missing tool configuration"}, 400
            if not step.step_config.get("config_ids"):
                logger.error(f"❌ Step {step.name} is missing config_ids")
                return {"error": f"Step {step.name} is missing config_ids"}, 400
            logger.info(f"✅ Step {step.name} validation passed")

        logger.info("💾 Creating pipeline in database...")
        pipeline = Pipeline(
                name=pipeline_data.name,
                description=pipeline_data.description,
                created_by=pipeline_data.created_by,
                created_at=datetime.utcnow()
            )
        pipeline_id = self.pipeline_repository.create_Pipeline(pipeline)
        logger.info(f"✅ Pipeline created in database with ID: {pipeline_id}")
        
        Pipeline_init = PipelineManager()
        i=1
        error_message = None
        
        try:
            logger.info("🔧 Creating pipeline steps...")
            for step_data in pipeline_data.step_list: 
                logger.info(f"📝 Creating step {i}: {step_data.name}")
                step = PipelineStepCreate(
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
                logger.info(f"✅ Step created with ID: {step_id}")
                
                logger.info(f"🔗 Creating configuration associations for step {step_id}...")
                for config_id in step_data.config_ids:
                    config_association = StepConfigurationAssociationCreate(
                            step_id=step_id,
                            step_config_id=config_id
                        )
                    self.StepConfigurationAssociation.add_association(config_association)
                    logger.info(f"✅ Association created: step {step_id} -> config {config_id}")
            
            logger.info("🔍 Checking for visualization steps...")
            has_visualization_step = any(
                step_data.step_config.get("config_type") == StepTypeEnum.DATA_VISUALIZATION 
                for step_data in pipeline_data.step_list
            )
            logger.info(f"📊 Has visualization step: {has_visualization_step}")
            
            logger.info("🏗️ Setting up pipeline manager...")
            for step_data in pipeline_data.step_list:
                github_repo_name = f"{pipeline_data.name}_{pipeline_id}_{step_data.order}"
                logger.info(f"🔧 Processing step with GitHub repo: {github_repo_name}")
                logger.info(f"🛠️ Tool: {step_data.step_config['tool']}")
                
                runner = Pipeline_init.get_runner(str(step_data.step_config["tool"]))
                logger.info(f"🏃 Runner type: {type(runner).__name__}")
                
                is_visual = step_data.step_config.get("config_type") == StepTypeEnum.DATA_VISUALIZATION
                logger.info(f"📊 Is visualization step: {is_visual}")
                
                Pipeline_init.add_step(github_repo_name, runner, step_data, is_visual)
                logger.info(f"✅ Step added to pipeline manager: {github_repo_name}")
            
            logger.info("🚀 Creating pipeline with Docker and GitHub...")
            dashboard_id = Pipeline_init.create_pipeline()
            logger.info(f"📊 Dashboard ID returned: {dashboard_id}")
            
            if has_visualization_step and dashboard_id:
                logger.info(f"🔗 Creating dashboard association: pipeline {pipeline_id} -> dashboard {dashboard_id}")
                self.dashboard_pipeline_association.create_association(pipeline_id, dashboard_id)
                logger.info("✅ Dashboard association created")
            
            logger.info(f"🎉 Pipeline '{pipeline_data.name}' created successfully with ID: {pipeline_id}")
            return {"message": "Pipeline created successfully", "pipeline_id": pipeline_id}, 201
            
        except Exception as e:
            logger.error(f"❌ Error during pipeline creation: {str(e)}")
            logger.error(f"📊 Pipeline ID: {pipeline_id}, Steps: {len(pipeline_data.step_list)}")
            
            try:
                logger.info("🧹 Attempting cleanup...")
                Pipeline_init.cleanup()
                logger.info("✅ Cleanup completed")
            except Exception as cleanup_error:
                logger.error(f"❌ Error during cleanup: {str(cleanup_error)}")
            
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