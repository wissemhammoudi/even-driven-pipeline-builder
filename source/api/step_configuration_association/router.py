from fastapi import APIRouter, Depends
from typing import List
from source.schema.step_stepconfi_association.schema import StepConfigurationAssociationCreate 
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.config.config import settings

configuration_router = APIRouter(
    prefix=f"{settings.api_prefix}/step-config-associations"
)

@configuration_router.post("/", response_model=StepConfigurationAssociationCreate)
def create_association(
    association: StepConfigurationAssociationCreate,
    StepConfigurationAssociationService:StepConfigurationAssociationService=Depends(StepConfigurationAssociationService)
):
    StepConfigurationAssociationService.add_association(association)
    return association

@configuration_router.get("/step/{step_id}/configs", response_model=List[int])
def get_configurations_for_step(
    step_id: int,
    StepConfigurationAssociationService:StepConfigurationAssociationService=Depends(StepConfigurationAssociationService)
):
    return StepConfigurationAssociationService.get_configurations_for_step(step_id)

@configuration_router.get("/config/{step_config_id}/steps", response_model=List[int])
def get_steps_for_configuration(
    step_config_id: int,
    StepConfigurationAssociationService:StepConfigurationAssociationService=Depends(StepConfigurationAssociationService)
):
    return StepConfigurationAssociationService.get_steps_for_configuration(step_config_id)

