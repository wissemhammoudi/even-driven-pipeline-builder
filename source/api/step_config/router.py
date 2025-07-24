from fastapi import APIRouter, Depends, HTTPException
from typing import List
from source.schema.step_config.schema import Step_Config
from source.service.step_config.service import configurationService
from source.config.config import settings

step_config_router = APIRouter(prefix=f"{settings.api_prefix}/stepConfig")

@step_config_router.get("/", response_model=List[Step_Config])
def get_step_config(configurationService: configurationService = Depends(configurationService)):
    return configurationService.list_Step_config()

@step_config_router.get("/types")
def get_step_types(configurationService: configurationService = Depends(configurationService)):
    return configurationService.get_all_step_types()

@step_config_router.get("/tools")
def get_tools_per_type(type: str,
                       configurationService: configurationService = Depends(configurationService)
                       ):
    return configurationService.get_all_step_tools_per_type(type)

@step_config_router.get("/plugins")
def get_plugins_per_tool_and_type(tool: str, type: str,
                                  configurationService: configurationService = Depends(configurationService)
                                  ):
    return configurationService.get_all_step_plugins_type_per_tool_per_type(tool, type)

@step_config_router.get("/toolsname")
def get_tools(configurationService: configurationService = Depends(configurationService)):
    return configurationService.get_all_tools_name()

@step_config_router.get("/configpertool")
def get_configs_per_tool( tool:str,
                        configurationService: configurationService = Depends(configurationService)
                         ):
    return configurationService.get_step_config_per_tool(tool)

@step_config_router.get("/configpertooltype")
def get_configs_per_tool( tool:str,type:str,pluginType:str,
                        configurationService: configurationService = Depends(configurationService)
):
    return configurationService.get_all_step_cpnfig_per_type_per_tool_per_plugintype(tool,type,pluginType)

@step_config_router.put("/{step_config_id}/deprecate",)
def deprecate_step_config(step_config_id:int ,
                        configurationService: configurationService = Depends(configurationService)

                          ):
    step_config = configurationService.get_by_id(step_config_id)
    if not step_config:
        raise HTTPException(status_code=404, detail="Step config not found")
    configurationService.mark_deprecated(step_config_id)
    return {"message":"step config marked depracted"}
