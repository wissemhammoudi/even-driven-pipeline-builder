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
from source.config.config import DockerConfig
from source.service.user.services import UserService
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
            return DockerConfig.meltano_docker_image
        elif tool in [ToolEnum.DLT, ToolEnum.SQLMESH, ToolEnum.SUPERSET]:
            return DockerConfig.dlt_sqlmesh_superset_docker_image
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
                print(f"Container stopped and removed successfully")
            except Exception as e:
                print(f"Error during container cleanup: {e}")

    def create_pipeline(self):
        """Creates pipeline with port exposure"""
        if not self.steps:
            raise HTTPException(status_code=400, detail="No steps found. Add steps first.")
        
        try:
            first_step_name, first_step = self._get_first_step()
            dashboard_id=None
            tool_type = first_step['config'].step_config.get('tool')
            image = self.get_image(tool_type)
            
            container = self.docker_manager.create_container(first_step_name, image, None)
            self.name = first_step_name
            
            for name, step in self.steps.items():
                step["runner"].container = container
                step["runner"].docker_manager = self.docker_manager  

            for name, step in self.steps.items():
                runner = step["runner"]
                if isinstance(runner, SupersetRunner):
                    dashboard_id = runner.config(step, name)
                else:
                    runner.config(step, name)
                
            container_name = f"{first_step_name.split('_')[0]}_{first_step_name.split('_')[1]}"
            workdir = f"/project/{container_name}"
            self.git_manager.push_to_github(self.docker_manager.get_container_name(), workdir)
            print(f"Pipeline '{first_step_name}' created successfully!")
            self._cleanup_container()
            return dashboard_id
            
        except Exception as e:
            print(f"Error occurred while creating pipeline:{e}")
            self._cleanup_container()

    def run_pipeline(self):
        """Run the pipeline and its steps"""
        try:
            if not self.steps:
                raise RuntimeError("No steps defined in pipeline")
            
            first_step_name, first_step = self._get_first_step()
            
            tool_type = first_step['config'].step_config.get('tool')
            image = self.get_image(tool_type)
            
            print(f"Starting container for pipeline '{first_step_name}'...")
            container = self.docker_manager.create_container(first_step_name, image, None)
            
            for name, step in self.steps.items():
                if step.get('isvisual'):
                    print(f"Skipping visualization step '{name}' during pipeline run")
                    continue
                step["runner"].container = container
                step["runner"].docker_manager = self.docker_manager  

            self.git_manager.pull_from_github(self.docker_manager.get_container_name())
            
            for step_name, step_data in self.steps.items():
                if step_data.get('isvisual'):
                    print(f"Skipping visualization step '{step_name}' during pipeline run")
                    continue
                
                print(f"Running step '{step_name}'...")
                runner = step_data['runner']
                runner.start(step_data, step_name)
                print(f"Step '{step_name}' completed successfully")
            
            print("Pipeline execution completed successfully")
            self._cleanup_container()
            
        except Exception as e:
            print(f"Error occurred while running pipeline: {e}")
            self._cleanup_container()
            raise RuntimeError(f"Failed to run pipeline: {str(e)}")
