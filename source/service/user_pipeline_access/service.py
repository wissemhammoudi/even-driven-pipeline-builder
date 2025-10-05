from typing import List, Optional, Dict, Any
from source.models.user_pipeline_access.model import UserPipelineAccess
from source.models.user.models import User
from source.models.pipeline.models import Pipeline
from source.repository.user_pipeline_access.repository import UserPipelineAccessRepository
from source.repository.pipeline.repository import PipelineRepository
from source.repository.user.repository import UserRepository
from source.schema.user_pipeline_access.schema import UserPipelineAccessCreate, UserPipelineAccessUpdate, UserPipelineAccessResponse
from source.schema.user_pipeline_access.schema import GrantType
from source.exceptions.exceptions import UserNotFoundError, PipelineNotFoundError
from source.service.PipelineManager.supersetclient import SupersetClient
from source.config.config import superset_config
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
                    base_url=superset_config.superset_url,
                    username=superset_config.superset_user,
                    password=superset_config.superset_password
                    )

    def _get_user_pipeline_ids(self, user_id: str) -> list:
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
        import logging
        logger = logging.getLogger(__name__)
        
        result = None
        try:
            logger.info(f"🔍 Looking for dashboard associations for pipeline {pipeline_id}")
            dashboard_assocs = self.dashboard_pipeline_association.get_by_pipeline_id(pipeline_id)
            
            if dashboard_assocs:
                dashboard_id = dashboard_assocs[0].dashboard_id
                logger.info(f"📊 Found dashboard ID: {dashboard_id}")
                
                superset_user_ids = []
                logger.info(f"👥 Processing {len(user_ids)} user IDs for Superset mapping")
                
                for user_id in user_ids:
                    logger.info(f"🔍 Looking up Superset account for user {user_id}")
                    assocs = self.user_superset_account_association_service.get_by_user_id(user_id)
                    logger.info(f"📋 Found {len(assocs)} Superset associations for user {user_id}")
                    superset_user_ids.extend([a.superset_user_id for a in assocs])
                
                logger.info(f"🎯 Total Superset user IDs: {superset_user_ids}")
                
                if superset_user_ids:
                    logger.info(f"🔐 Authenticating with Superset client")
                    auth_result = self.superset_client.authenticate()
                    logger.info(f"🔐 Superset authentication result: {auth_result}")
                    
                    if auth_result:
                        logger.info(f"✅ Successfully authenticated with Superset")
                        logger.info(f"👥 Updating dashboard owners: {superset_user_ids}, add={add}")
                        result = self.superset_client.update_dashboard_owners(dashboard_id, superset_user_ids, add=add)
                        logger.info(f"📡 Superset update result: {result}")
                        
                        if result is not None and isinstance(result, dict) and 'success' in result:
                            logger.info(f"✅ Superset dashboard owners updated successfully")
                            return result
                        else:
                            logger.error(f"❌ Unexpected response from Superset client: {result}")
                            return {"success": False, "error": "Unexpected response from Superset client"}
                    else:
                        logger.error(f"❌ Failed to authenticate with Superset")
                        return {"success": False, "error": "Failed to authenticate with Superset"}
                else:
                    logger.warning(f"⚠️ No Superset users found for given user_ids: {user_ids}")
                    return {"success": False, "error": "No superset users found for given user_ids"}
            else:
                logger.warning(f"⚠️ No dashboard found for pipeline {pipeline_id}")
                return {"success": False, "error": "No dashboard found for given pipeline_id"}
        except Exception as e:
            logger.error(f"❌ Exception in _update_superset_dashboard_owners: {str(e)}")
            import traceback
            logger.error(f"📊 Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
        
    def bulk_grant_access(self, pipeline_id: int, user_ids: List[str], grant_type: GrantType, granted_by: str) -> List[UserPipelineAccessResponse]:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔧 Starting bulk grant access for pipeline {pipeline_id}")
        logger.info(f"👥 User IDs: {user_ids}")
        logger.info(f"🎯 Grant type: {grant_type}")
        logger.info(f"👤 Granted by: {granted_by}")
        
        results = []
        for user_id in user_ids:
            try:
                logger.info(f"📝 Processing access for user {user_id}")
                access_data = UserPipelineAccessCreate(
                    user_id=user_id,
                    pipeline_id=pipeline_id,
                    grant_type=grant_type,
                    granted_by=granted_by
                )
                existing_access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
                if existing_access:
                    logger.info(f"🔄 Updating existing access for user {user_id}")
                    updated_access = self.access_repository.update_access(
                        user_id,
                        pipeline_id,
                        grant_type,
                        granted_by
                    )
                    results.append(UserPipelineAccessResponse.from_orm(updated_access))
                else:
                    logger.info(f"➕ Creating new access for user {user_id}")
                    new_access = UserPipelineAccess(
                        user_id=user_id,
                        pipeline_id=pipeline_id,
                        grant_type=grant_type,
                        granted_by=granted_by
                    )
                    created_access = self.access_repository.create_access(new_access)
                    results.append(UserPipelineAccessResponse.from_orm(created_access))
            except Exception as e:
                logger.error(f"❌ Error processing access for user {user_id}: {str(e)}")
                continue
        
        logger.info(f"📊 Database access operations completed. Results: {len(results)}")
        
        try:
            logger.info(f"🌐 Updating Superset dashboard owners for pipeline {pipeline_id}")
            result = self._update_superset_dashboard_owners(pipeline_id, user_ids, add=True)
            logger.info(f"📡 Superset update result: {result}")
            
            if not result.get("success"):
                logger.warning(f"⚠️ Superset dashboard update failed: {result.get('error')}")
                # Don't raise exception, just log the warning
                logger.warning("⚠️ Continuing without Superset dashboard update")
            else:
                logger.info("✅ Superset dashboard owners updated successfully")
        except Exception as e:
            logger.error(f"❌ Exception during Superset dashboard update: {str(e)}")
            logger.warning("⚠️ Continuing without Superset dashboard update")

        logger.info(f"🎉 Bulk grant access completed successfully. {len(results)} users processed.")
        return results

    def bulk_revoke_access(self, pipeline_id: int, user_ids: List[str]) -> Dict[str, int]:
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
    def get_pipelines_for_user(self, user_id: str) -> List[Pipeline]:
        return self.access_repository.get_pipelines_for_user(user_id)

    def can_start_pipeline(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True        
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_start_visualization(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_manage_access(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER]

    def can_edit_pipeline(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type in [GrantType.OWNER, GrantType.VIEW]

    def can_delete_pipeline(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        if not access:
            return False
        return access.grant_type == GrantType.OWNER

    def can_view_pipeline(self, user_id: str, pipeline_id: int) -> bool:
        user = self.user_repository.get_user_by_id(user_id)
        if user and user.role.value == UserRole.admin:
            return True
        access = self.access_repository.get_access_by_user_and_pipeline(user_id, pipeline_id)
        return access is not None 