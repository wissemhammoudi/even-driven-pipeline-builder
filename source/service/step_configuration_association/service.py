
from typing import List
from source.repository.step_configuration_association.repository import StepConfigurationAssociationRepository
from source.models.step_configuration_association.model import (StepConfigurationAssociation
)

class StepConfigurationAssociationService:
    def __init__(self):
        self.repository = StepConfigurationAssociationRepository()

    def add_association(self, association_data):
        association_model = StepConfigurationAssociation(
            step_id=association_data.step_id,
            step_config_id=association_data.step_config_id
        )        
        return self.repository.create_association(association_model,)

    def get_steps_for_configuration(self, step_id: int) -> List[int]:
        return self.repository.get_steps_for_configuration(step_id,)

    def get_steps_ids_by_configuration_id(self, step_config_id: int) -> List[int]:
        return self.repository.get_steps_ids_by_configuration_id(step_config_id,)
    def delete_by_step_id(self, step_id:int):
        return self.repository.delete_by_step_id(step_id)

    def rollback(self):
        self.repository.rollback()
