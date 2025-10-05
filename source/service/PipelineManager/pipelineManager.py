import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from source.service.PipelineManager.dockermanager import DockerManager
from source.service.PipelineManager.githubmanager import GitManager
from source.service.PipelineManager.interface import BaseStepRunner
from source.models.pipeline_step.models import Step
from source.service.PipelineManager.meltano import MeltanoRunner
from source.service.PipelineManager.dlt import DltRunner
from source.service.PipelineManager.sqlmesh import SqlmeshRunner
from source.service.PipelineManager.superset import SupersetRunner
from source.schema.pipeline.schema import ToolEnum, StepTypeEnum
from source.config.config import docker_config
from source.service.user.services import UserService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class PipelineManager:
    """Unified pipeline manager that orchestrates Docker and Git operations"""
    
    def __init__(self):
        self.docker_manager = DockerManager()
        self.git_manager = GitManager(self.docker_manager)
        self.steps = {}
        self.visualization_step = None
        self.visualization_container = None
        self.name = None
        self.user_service = UserService()

    def add_step(self, step_name: str, runner: BaseStepRunner, stepconfig: Step, isvisual: bool = None):
        """Add a step to the pipeline"""
        if stepconfig.step_config.get("config_type") == StepTypeEnum.DATA_VISUALIZATION:
            if self.visualization_step is not None and self.visualization_step != step_name:
                raise ValueError("Pipeline can only have one visualization step")
            self.visualization_step = step_name
            isvisual = True
        
        self.steps[step_name] = {
            "runner": runner,
            'config': stepconfig,
            'isvisual': isvisual
        }
        print(f"Step '{step_name}' added.")

    def delete_step(self, step_name: str):
        """Remove a step from the pipeline"""
        if step_name not in self.steps:
            raise KeyError(f"Step '{step_name}' not found in pipeline")
            
        if self.visualization_step == step_name:
            self.visualization_step = None
            
        del self.steps[step_name]
        print(f"Step '{step_name}' deleted.")

    def get_runner(self, tool: str) -> BaseStepRunner:
        """Get appropriate runner for the tool"""
        runner_map = {
            ToolEnum.MELTANO: MeltanoRunner,
            ToolEnum.DLT: DltRunner,
            ToolEnum.SQLMESH: SqlmeshRunner,
            ToolEnum.SUPERSET: SupersetRunner
        }
        
        if tool not in runner_map:
            raise ValueError(f"Unsupported step type: {tool}")
            
        return runner_map[tool]()

    def get_image(self, tool: str) -> str:
        """Get Docker image for the tool"""
        if tool == ToolEnum.MELTANO:
            return docker_config.meltano_docker_image
        elif tool in [ToolEnum.DLT, ToolEnum.SQLMESH, ToolEnum.SUPERSET]:
            return docker_config.dlt_sqlmesh_superset_docker_image
        else:
            raise ValueError(f"Unsupported step type: {tool}")

    def get_steps(self) -> Dict[str, Any]:
        """Get all pipeline steps"""
        return self.steps

    def get_visualization_step(self) -> Optional[str]:
        """Get the visualization step name if exists"""
        return self.visualization_step

    def _get_first_step(self):
        """Get the first non-visualization step, or first step if all are visual"""
        first_step_name = None
        first_step = None
        
        for name, step in self.steps.items():
            if not step.get('isvisual', False):
                first_step_name = name
                first_step = step
                break
        
        if not first_step:
            first_step_name = next(iter(self.steps))
            first_step = self.steps[first_step_name]
        
        return first_step_name, first_step

    def _cleanup_container(self):
        """Clean up container resources"""
        if self.docker_manager.container:
            try:
                self.docker_manager.stop_container()
                logger.info(f"Container stopped and removed successfully")
            except Exception as e:
                logger.error(f"Error during container cleanup: {e}")
    
    def cleanup(self):
        """Public cleanup method for external use"""
        logger.info("🧹 Starting pipeline cleanup...")
        self._cleanup_container()
        logger.info("✅ Pipeline cleanup completed")

    def create_pipeline(self):
        """Creates pipeline with port exposure"""
        logger.info("🚀 Starting pipeline creation process")
        
        if not self.steps:
            logger.error("❌ No steps found. Add steps first.")
            raise HTTPException(status_code=400, detail="No steps found. Add steps first.")
        
        logger.info(f"📋 Pipeline has {len(self.steps)} steps: {list(self.steps.keys())}")
        
        try:
            first_step_name, first_step = self._get_first_step()
            logger.info(f"🎯 First step: {first_step_name}")
            
            dashboard_id=None
            tool_type = first_step['config'].step_config.get('tool')
            logger.info(f"🔧 Tool type: {tool_type}")
            
            image = self.get_image(tool_type)
            logger.info(f"🐳 Docker image: {image}")
            
            logger.info(f"📦 Creating Docker container: {first_step_name}")
            container = self.docker_manager.create_container(first_step_name, image, None)
            self.name = first_step_name
            
            logger.info("🔗 Setting up runners for all steps...")
            for name, step in self.steps.items():
                logger.info(f"⚙️ Configuring runner for step: {name}")
                step["runner"].container = container
                step["runner"].docker_manager = self.docker_manager  

            logger.info("🎛️ Configuring step runners...")
            for name, step in self.steps.items():
                runner = step["runner"]
                logger.info(f"🔧 Configuring step '{name}' with runner: {type(runner).__name__}")
                try:
                    if isinstance(runner, SupersetRunner):
                        logger.info(f"📊 Configuring Superset dashboard for step: {name}")
                        dashboard_id = runner.config(step, name)
                        logger.info(f"📊 Dashboard ID: {dashboard_id}")
                    else:
                        runner.config(step, name)
                except Exception as e:
                    logger.error(f"❌ Error configuring step '{name}': {str(e)}")
                    if isinstance(runner, SupersetRunner):
                        logger.warning(f"⚠️ Superset configuration failed for step '{name}', continuing without dashboard")
                        dashboard_id = None
                    else:
                        raise  # Re-raise for non-Superset errors
                
            container_name = f"{first_step_name.split('_')[0]}_{first_step_name.split('_')[1]}"
            workdir = f"/project/{container_name}"
            logger.info(f"📁 Container name: {container_name}")
            logger.info(f"📁 Working directory: {workdir}")
            
            logger.info("🌐 Pushing to GitHub...")
            try:
                self.git_manager.push_to_github(self.docker_manager.get_container_name(), workdir)
                logger.info("✅ GitHub push completed successfully")
            except Exception as e:
                logger.error(f"❌ GitHub push failed: {str(e)}")
                logger.warning("⚠️ Continuing pipeline creation despite GitHub push failure")
            
            logger.info(f"✅ Pipeline '{first_step_name}' created successfully!")
            self._cleanup_container()
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Error occurred while creating pipeline: {str(e)}")
            logger.error(f"📊 Pipeline name: {self.name}, Steps: {list(self.steps.keys()) if self.steps else 'None'}")
            self._cleanup_container()
            raise

    def run_pipeline(self):
        """Run the pipeline and its steps"""
        logger.info("🏃 Starting pipeline execution")
        
        try:
            if not self.steps:
                logger.error("❌ No steps defined in pipeline")
                raise RuntimeError("No steps defined in pipeline")
            
            first_step_name, first_step = self._get_first_step()
            logger.info(f"🎯 First step: {first_step_name}")
            
            tool_type = first_step['config'].step_config.get('tool')
            image = self.get_image(tool_type)
            logger.info(f"🔧 Tool type: {tool_type}, Image: {image}")
            
            logger.info(f"🐳 Starting container for pipeline '{first_step_name}'...")
            container = self.docker_manager.create_container(first_step_name, image, None)
            
            logger.info("🔗 Setting up runners for non-visualization steps...")
            for name, step in self.steps.items():
                if step.get('isvisual'):
                    logger.info(f"⏭️ Skipping visualization step '{name}' during pipeline run")
                    continue
                logger.info(f"⚙️ Configuring runner for step: {name}")
                step["runner"].container = container
                step["runner"].docker_manager = self.docker_manager  

            logger.info("📥 Pulling code from GitHub...")
            self.git_manager.pull_from_github(self.docker_manager.get_container_name())
            
            logger.info("🏃 Executing pipeline steps...")
            for step_name, step_data in self.steps.items():
                if step_data.get('isvisual'):
                    logger.info(f"⏭️ Skipping visualization step '{step_name}' during pipeline run")
                    continue
                
                logger.info(f"🔄 Running step '{step_name}'...")
                runner = step_data['runner']
                runner.start(step_data, step_name)
                logger.info(f"✅ Step '{step_name}' completed successfully")
            
            logger.info("🎉 Pipeline execution completed successfully")
            self._cleanup_container()
            
        except Exception as e:
            logger.error(f"❌ Error occurred while running pipeline: {str(e)}")
            logger.error(f"📊 Pipeline name: {self.name}, Steps: {list(self.steps.keys()) if self.steps else 'None'}")
            self._cleanup_container()
            raise RuntimeError(f"Failed to run pipeline: {str(e)}")
