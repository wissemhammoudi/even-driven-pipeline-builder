from source.schema.pipeline_run.schema import PipelineRunCreate
from source.models.pipeline_run.model import PipelineRun
from source.repository.pipeline_run.repository import PipelineRunRepository
from source.service.PipelineManager.pipelineManager import PipelineManager
from source.service.pipeline_step.service import StepService
from source.service.pipeline.service import PipelineService
import datetime
from source.repository.database import get_db
from source.schema.pipeline.schema import PipelineStatusEnum

database = get_db()

class PipelineRunService:
    def __init__(self):
        self.db = database
        self.repo = PipelineRunRepository()
        self.step_service = StepService()
        self.pipline_service=PipelineService()
        
    def get_pipeline_runs_by_pipeline_id(self,pipeline_id):
        return self.repo.get_pipeline_run_by_pipeline_id(pipeline_id)
    
    def start_pipeline(self, run: PipelineRunCreate):
        start_time = datetime.datetime.now()
        status = "FAILED"
        end_time = None
        container_names = []
        pipeline_runner = PipelineManager()
        pipeline_run = None
        error_message = None
        
        try:
            pipeline_data = self.pipline_service.get_pipline_by_id(run.pipeline_id)
            if not pipeline_data:
                error_message = "Pipeline not found"
                raise ValueError(error_message)
            
            if pipeline_data.status == PipelineStatusEnum.broken:
                error_message = "Cannot start pipeline: Pipeline is marked as broken due to schema changes"
                raise ValueError(error_message)
            
            steps_data = self.step_service.get_steps_by_pipeline(run.pipeline_id)
            if not steps_data:
                error_message = "No steps found for this pipeline"
                raise ValueError(error_message)
            
            pipeline_run = self.repo.create(PipelineRun(
                pipeline_id=run.pipeline_id,
                created_by=run.user_id,
                pipeline_run="RUNNING"  
            ))
            for step in steps_data:
                stepconfig = step.step_config
                if stepconfig:
                    try:
                        github_repo_name = f"{pipeline_data.name}_{str(run.pipeline_id)}_{str(step.order)}"
                        container_names.append(github_repo_name)
                        runner = pipeline_runner.get_runner(str(step.step_config["tool"]))
                        pipeline_runner.add_step(github_repo_name, runner, step)
                    except Exception as step_error:
                        error_message = f"Error processing step {step.order}: {str(step_error)}"
                        raise RuntimeError(error_message)
            
            try:
                pipeline_runner.run_pipeline()
                status = "SUCCESS"
            except Exception as pipeline_error:
                error_message = f"Pipeline start failed: {str(pipeline_error)}"
                raise RuntimeError(error_message)
        
        except Exception as e:
            status = "FAILED"
            error_message = str(e) if not error_message else error_message
            print(f"Error running pipeline: {error_message}")
            
            try:
                pipeline_runner.cleanup()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {str(cleanup_error)}")
        
        finally:
            end_time = datetime.datetime.now()
            
            if pipeline_run:
                pipeline_run.start_time = start_time
                pipeline_run.end_time = end_time
                pipeline_run.status = status
                pipeline_run.pipeline_run = container_names[0] if container_names else None
                if error_message:
                    pipeline_run.error_message = error_message
                self.repo.update(pipeline_run)
        
        response_data = {
            "status": status,
            "pipeline_run": pipeline_run,
            "error": error_message if status == "FAILED" else None
        }
        
        if status == "SUCCESS":
            return response_data, 200
        else:
            return response_data, 500
           