from source.repository.step_config.repository import configurationRepository
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.service.pipeline_step.service import StepService
from source.repository.pipeline.repository import PipelineRepository

class configurationService:
    def __init__(self):
        self.repository = configurationRepository()
        self.stepConfigAssociationService =StepConfigurationAssociationService()
        self.stepSerivce=StepService()
        self.pipelineRepotory =PipelineRepository()

    def list_Step_config(self):
        return self.repository.get_all_step_configs()
    
    def get_by_id(self, step_config_id: int) :
        return self.repository.get_by_id(step_config_id,)
    
    def get_all_step_types(self):
        return self.repository.get_all_step_types()

    def get_all_step_tools_per_type(self,type:str):
        return self.repository.get_all_tools(type,)
    
    def get_all_step_plugins_type_per_tool_per_type(self,tool:str,type:str):
        return self.repository.get_all_plugin_types(tool,type,)
    
    def get_all_step_cpnfig_per_type_per_tool_per_plugintype(self,tool:str,type:str,pluginType:str):
        return self.repository.get_step_config_by_type_tool_plugin_type(type,tool,pluginType,)
    
    def get_all_tools_name(self):
        return self.repository.get_all_tools_name()
    
    def get_step_config_per_tool(self,tool:str):
        return self.repository.get_step_config_per_tool(tool,)                  

    def mark_deprecated(self, step_config_id: int):
        steps_ids=self.stepConfigAssociationService.get_steps_ids_by_configuration_id(step_config_id,)
        if steps_ids:
            piplines_ids=self.stepSerivce.get_piplines_ids(steps_ids,)
            self.stepSerivce.mark_deprecated(steps_ids,)
            if piplines_ids:
                for piplines_id in piplines_ids:
                    self.pipelineRepotory.mark_deprecated(piplines_id, )
        self.repository.mark_deprecated(step_config_id,)