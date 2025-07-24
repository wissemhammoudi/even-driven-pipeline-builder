from typing import List, Optional
from source.models.user_pipeline_access.model import UserPipelineAccess
from source.models.user.models import User
from source.models.pipeline.models import Pipeline
from source.repository.database import get_db
from source.schema.user_pipeline_acess.schema import GrantType

database = get_db()

class UserPipelineAccessRepository:
    def __init__(self):
        self.db = database

    def create_access(self, access: UserPipelineAccess) -> UserPipelineAccess:
        try:
            self.db.add(access)
            self.db.commit()
            self.db.refresh(access)
            return access
        except Exception as e:
            self.db.rollback()
            raise e

    def get_access_by_user_and_pipeline(self, user_id: int, pipeline_id: int) -> Optional[UserPipelineAccess]:
        return self.db.query(UserPipelineAccess).filter(
            UserPipelineAccess.user_id == user_id,
            UserPipelineAccess.pipeline_id == pipeline_id
        ).first()

    def get_pipeline_accesses(self, pipeline_id: int) -> List[UserPipelineAccess]:
        return self.db.query(UserPipelineAccess).filter(
            UserPipelineAccess.pipeline_id == pipeline_id
        ).all()

    def update_access(self, user_id: int, pipeline_id: int, grant_type: GrantType, granted_by: int) -> Optional[UserPipelineAccess]:
        try:
            access = self.get_access_by_user_and_pipeline(user_id, pipeline_id)
            if access:
                access.grant_type = grant_type
                access.granted_by = granted_by
                self.db.commit()
                self.db.refresh(access)
                return access
            return None
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_access(self, user_id: int, pipeline_id: int) -> bool:
        try:
            access = self.get_access_by_user_and_pipeline(user_id, pipeline_id)
            if access:
                self.db.delete(access)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def get_pipelines_for_user(self, user_id: int) -> List[Pipeline]:
        return self.db.query(Pipeline).join(UserPipelineAccess).filter(
            UserPipelineAccess.user_id == user_id,
            Pipeline.is_deleted == False
        ).all()

    def get_users_for_pipeline(self, pipeline_id: int) -> List[User]:
        return self.db.query(User).join(UserPipelineAccess, User.user_id == UserPipelineAccess.user_id).filter(
            UserPipelineAccess.pipeline_id == pipeline_id,
            User.is_deleted == False
        ).all() 