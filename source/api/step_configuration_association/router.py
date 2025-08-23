from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from source.schema.step_configuration_association.schema import StepConfigurationAssociationCreate, StepConfigurationAssociationUpdate, StepConfigurationAssociationResponse
from source.service.step_configuration_association.service import StepConfigurationAssociationService
from source.exceptions.exceptions import StepConfigurationAssociationNotFoundError
from source.config.config import api_config
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from source.service.user.services import UserService
from source.schema.user.schemas import UserRole     
from source.service.authentication.keycloak_auth import get_current_user, require_user_role, require_admin_role 

configuration_router = APIRouter(
    prefix=f"{api_config.api_prefix}/step-config-associations"
)

@configuration_router.post("/", response_model=StepConfigurationAssociationCreate)
def create_association(
    association: StepConfigurationAssociationCreate,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(require_admin_role)
):
    StepConfigurationAssociationService.add_association(association)
    return association

@configuration_router.get("/step/{step_id}/configs", response_model=List[int])
def get_configurations_for_step(
    step_id: int,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(require_user_role)
):
    return StepConfigurationAssociationService.get_configurations_for_step(step_id)

@configuration_router.get("/config/{step_config_id}/steps", response_model=List[int])
def get_steps_for_configuration(
    step_config_id: int,
    StepConfigurationAssociationService: StepConfigurationAssociationService = Depends(StepConfigurationAssociationService),
    current_user: dict = Depends(require_user_role)
):
    return StepConfigurationAssociationService.get_steps_for_configuration(step_config_id)

