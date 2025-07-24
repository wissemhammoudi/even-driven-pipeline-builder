from typing import List, Optional, Dict, Any
from source.models.user_pipeline_access.model import UserPipelineAccess
from source.models.user.models import User
from source.models.pipeline.models import Pipeline
from source.repository.user_pipeline_access.repository import UserPipelineAccessRepository
from source.repository.pipeline.repository import PipelineRepository
from source.repository.user.repository import UserRepository
from source.schema.user_pipeline_acess.schema import UserPipelineAccessCreate, UserPipelineAccessUpdate, UserPipelineAccessResponse
from source.schema.user_pipeline_acess.schema import GrantType
from source.exceptions.exceptions import UserNotFoundError, PipelineNotFoundError
from source.service.PipelineManager.supersetclient import SupersetClient
from source.config.config import SupersetConfig
from source.schema.user.schemas import UserRole
from source.service.dashboard_pipeline_association.service import DashboardPipelineAssociationService
from source.service.user_superset_account_association.service import UserSupersetAccountAssociationService
class UserPipelineAccessService:
    def __init__(self):
        self.access_repository = UserPipelineAccessRepository()
        self.pipeline_repository = PipelineRepository()
        self.user_repository = UserRepository()
        self.dashboard_pipeline_association=DashboardPipelineAssociationService()
        self.user_superset_account_association_service=UserSupersetAccountAssociationService()
        self.superset_client=SupersetClient(
                    base_url=SupersetConfig.superset_url,
                    username=SupersetConfig.superset_user,
                    password=SupersetConfig.superset_password
                    )

    def _get_user_pipeline_ids(self, user_id: int) -> list:
        try:
            user = self.user_repository.get_active_user_by_id(user_id)

            if not user:
                return []

            is_admin = user.role.value == "admin" if hasattr(user.role, 'value') else False

            if is_admin:
                all_pipeline_ids = self.pipeline_repository.get_all_pipelines_ids()
                return all_pipeline_ids
            else:
                accessible_pipelines = self.get_pipelines_for_user(user_id)
                return [pipeline.pipeline_id for pipeline in accessible_pipelines]

        except Exception as e:
            return []
        
    def _update_superset_dashboard_owners(self, pipeline_id: int, user_ids: list, add: bool):
        result = None
        try:
            dashboard_assocs = self.dashboard_pipeline_association.get_by_pipeline_id(pipeline_id)
            if dashboard_assocs:
                dashboard_id = dashboard_assocs[0].dashboard_id
                superset_user_ids = []
                for user_id in user_ids:
                    assocs = self.user_superset_account_association_service.get_by_user_id(user_id)
                    superset_user_ids.extend([a.superset_user_id for a in assocs])
                if superset_user_ids:
                    self.superset_client.authenticate()
                    result = self.superset_client.update_dashboard_owners(dashboard_id, superset_user_ids, add=add)
                    if result is not None and isinstance(result, dict) and 'success' in result:
                        return result
                    else:
                        return {"success": False, "error": "Unexpected response from Superset client"}
                else:
                    return {"success": False, "error": "No superset users found for given user_ids"}
            else:
                return {"success": False, "error": "No dashboard found for given pipeline_id"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def bulk_grant_access(self, pipeline_id: int, user_ids: List[int], grant_type: GrantType, granted_by: int) -> List[UserPipelineAccessResponse]:
        results = []
        for user_id in user_ids:
            try:
                access_data = UserPipelineAccessCreate(
                    user_id=user_id,
                    pipeline_id=pipeline_id,
                    grant_type=grant_type,
                    granted_by=granted_by
                )
                existing_access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
                if existing_access:
                    updated_access = self.access_repository.update_access(
                        user_id,
                        pipeline_id,
                        grant_type,
                        granted_by
                    )
                    results.append(UserPipelineAccessResponse.from_orm(updated_access))
                else:
                    new_access = UserPipelineAccess(
                        user_id=user_id,
                        pipeline_id=pipeline_id,
                        grant_type=grant_type,
                        granted_by=granted_by
                    )
                    created_access = self.access_repository.create_access(new_access)
                    results.append(UserPipelineAccessResponse.from_orm(created_access))
            except Exception:
                continue
        result = self._update_superset_dashboard_owners(pipeline_id, user_ids, add=True)
        if not result.get("success"):
            raise Exception(f"Failed to update Superset dashboard owners for pipeline {pipeline_id}{result.get('error')}")

        return results

    def bulk_revoke_access(self, pipeline_id: int, user_ids: List[int]) -> Dict[str, int]:
        success_count = 0
        failure_count = 0
        for user_id in user_ids:
            try:
                if self.access_repository.delete_access(user_id, pipeline_id):
                    success_count += 1
                else:
                    failure_count += 1
            except Exception:
                failure_count += 1

        result = self._update_superset_dashboard_owners(pipeline_id, user_ids, add=False)
        if not result.get("success"):
            raise Exception(f"Failed to update Superset dashboard owners for pipeline {pipeline_id}")

        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "total_processed": len(user_ids)
        }
    
    def update_access(self, access_data: UserPipelineAccessUpdate) -> UserPipelineAccessResponse:
        user = self.user_repository.get_user_by_id(access_data.user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {access_data.user_id} not found")

        pipeline = self.pipeline_repository.get_pipline_by_id(access_data.pipeline_id)
        if not pipeline:
            raise PipelineNotFoundError(f"Pipeline with ID {access_data.pipeline_id} not found")

        updated_access = self.access_repository.update_access(
            access_data.user_id,
            access_data.pipeline_id,
            access_data.grant_type,
            access_data.granted_by
        )
        if not updated_access:
            raise Exception(f"Access record not found for user {access_data.user_id} and pipeline {access_data.pipeline_id}")
        add_owner = access_data.grant_type == GrantType.OWNER
        self._setup_superset_user_access(user, pipeline, add=add_owner)

        return UserPipelineAccessResponse.from_orm(updated_access) 
    def get_users_for_pipeline(self, pipeline_id: int) -> List[User]:
        return self.access_repository.get_users_for_pipeline(pipeline_id)
    def get_pipelines_for_user(self, user_id: int) -> List[Pipeline]:
        return self.access_repository.get_pipelines_for_user(user_id)

    def can_start_pipeline(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True        
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_start_visualization(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_manage_access(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER]

    def can_edit_pipeline(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_delete_pipeline(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type == GrantType.OWNER

    def can_view_pipeline(self, user_id: int, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        return access is not None 