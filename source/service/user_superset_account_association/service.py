from source.repository.user_superset_account_association.repository import UserSupersetAccountAssociationRepository

class UserSupersetAccountAssociationService:
    def __init__(self):
        self.repository = UserSupersetAccountAssociationRepository()

    def add_association(self, user_id: int, superset_user_id: int):
        return self.repository.add_association(user_id, superset_user_id)

    def get_by_user_id(self, user_id: int):
        return self.repository.get_by_user_id(user_id) 