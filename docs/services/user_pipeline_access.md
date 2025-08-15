# User Pipeline Access Service

This module manages user access control for pipelines, including granting, revoking, and checking permissions, as well as integrating with Superset dashboard ownership.

---

## Main Class

### UserPipelineAccessService
Handles all business logic related to user access to pipelines, including bulk operations, permission checks, and dashboard integration.

**Key Methods:**
- `__init__(self)`: Initializes repositories and Superset integration.
- `bulk_grant_access(self, pipeline_id, user_ids, grant_type, granted_by)`: Grants access to multiple users for a pipeline.
- `bulk_revoke_access(self, pipeline_id, user_ids)`: Revokes access for multiple users from a pipeline.
- `update_access(self, access_data)`: Updates access for a user and pipeline.
- `get_users_for_pipeline(self, pipeline_id)`: Returns all users with access to a pipeline.
- `get_pipelines_for_user(self, user_id)`: Returns all pipelines a user can access.
- `can_start_pipeline(self, user_id, pipeline_id)`: Checks if a user can start a pipeline.
- `can_start_visualization(self, user_id, pipeline_id)`: Checks if a user can start a visualization.
- `can_manage_access(self, user_id, pipeline_id)`: Checks if a user can manage access for a pipeline.
- `can_edit_pipeline(self, user_id, pipeline_id)`: Checks if a user can edit a pipeline.
- `can_delete_pipeline(self, user_id, pipeline_id)`: Checks if a user can delete a pipeline.
- `can_view_pipeline(self, user_id, pipeline_id)`: Checks if a user can view a pipeline.

---

Use this module to:
- Manage user access and permissions for pipelines.
- Integrate access control with Superset dashboard ownership.
- Support secure, role-based access to pipeline features and data. 