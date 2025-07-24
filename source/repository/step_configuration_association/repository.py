from source.models.step_configuration_association.model import StepConfigurationAssociation
from typing import List
from source.repository.database import get_db
from sqlalchemy import select 
database= get_db()
class StepConfigurationAssociationRepository:
    def __init__(self):
        self.db = database

    def create_association(self, association) -> None:
        try:
            self.db.add(association)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_configuration_ids_by_step_id(self, step_id: int) -> List[int]:
        stmt = (
            select(StepConfigurationAssociation.step_config_id)
            .where(StepConfigurationAssociation.step_id == step_id)
        )
        return self.db.scalars(stmt).all() 

    def get_steps_ids_by_configuration_id(self, step_config_id: int) -> List[int]:

        stmt = (
            select(StepConfigurationAssociation.step_id)
            .where(StepConfigurationAssociation.step_config_id == step_config_id)
        )
        return self.db.scalars(stmt).all()
    
    def delete_by_step_id(self,step_id:int):
        associations = (
            self.db.query(StepConfigurationAssociation)
            .filter(StepConfigurationAssociation.step_id == step_id)
            .all()
        )
        for assoc in associations:
            self.db.delete(assoc)
        self.db.commit()

    
    def rollback(self):
        self.db.rollback()
