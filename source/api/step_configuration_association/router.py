from fastapi import APIRouter, Depends
from typing import List
from source.schema.step_configuration_association.schema import StepConfigurationAssociationCreate
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.config.config import api_config
from source.service.authentication.keycloak_auth import KeycloakAuthService

configuration_router = APIRouter(
    prefix=f"{api_config.api_prefix}/step-config-associations"
)

@configuration_router.post("/", response_model=StepConfigurationAssociationCreate)
def create_association(
    association: StepConfigurationAssociationCreate,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(KeycloakAuthService.require_admin_role)
):
    StepConfigurationAssociationService.add_association(association)
    return association

@configuration_router.get("/step/{step_id}/configs", response_model=List[int])
def get_configurations_for_step(
    step_id: int,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(KeycloakAuthService.require_user_role)
):
    return StepConfigurationAssociationService.get_configurations_for_step(step_id)

@configuration_router.get("/config/{step_config_id}/steps", response_model=List[int])
def get_steps_for_configuration(
    step_config_id: int,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(KeycloakAuthService.require_user_role)
):
    return StepConfigurationAssociationService.get_steps_for_configuration(step_config_id)

