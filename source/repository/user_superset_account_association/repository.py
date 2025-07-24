from source.models.user_superset_account_association.model import UserSupersetAccountAssociation
from source.repository.database import get_db
from sqlalchemy.orm import Session

class UserSupersetAccountAssociationRepository:
    def __init__(self):
        self.db: Session = get_db()

    def add_association(self, user_id: int, superset_user_id: int) -> UserSupersetAccountAssociation:
        association = UserSupersetAccountAssociation(user_id=user_id, superset_user_id=superset_user_id)
        self.db.add(association)
        self.db.commit()
        self.db.refresh(association)
        return association

    def get_by_user_id(self, user_id: int):
        return self.db.query(UserSupersetAccountAssociation).filter_by(user_id=user_id).all() 