# Pipeline Service

This module provides the core logic for creating, managing, updating, and deleting data pipelines, as well as managing their steps and associations.

---

## Main Class

### PipelineService
Handles all business logic related to pipelines, including creation, deletion, step management, and integration with other services (step configuration, dashboard, etc.).

**Key Methods:**
- `__init__(self)`: Initializes repositories and related services.
- `list_pipelines(self, user_id, offset=0, limit=10, deprecated=False, name=None, created_date=None)`: Returns a paginated list of pipelines for a user.
- `list_all_pipelines_ids(self)`: Returns all pipeline IDs.
- `get_pipeline_by_id(self, pipeline_id)`: Retrieves a pipeline by its ID.
- `list_pipelines_by_user(self, user_id)`: Lists all pipelines for a given user.
- `create_pipeline(self, pipeline_data)`: Creates a new pipeline, its steps, and their associations. Handles validation and error cleanup.
- `delete_pipeline(self, pipeline_data)`: Soft-deletes a pipeline and its steps.
- `get_pipeline_steps(self, pipeline_id)`: Returns the step IDs for a pipeline.
- `add_step_to_pipeline(self, step_data)`: Adds a step to a pipeline.
- `delete_steps_from_pipeline(self, step_data)`: Removes a step from a pipeline.
- `update_pipeline(self, pipeline_data)`: Updates pipeline metadata (name, description).
- `mark_deprecated(self, pipeline_id, stepsids)`: Marks a pipeline as deprecated.
- `get_pipeline_steps_details(self, pipeline_id)`: Returns detailed information about all steps in a pipeline.

---

Use this module to:
- Create and manage pipelines and their steps.
- Integrate with step configuration, dashboard, and other pipeline-related services.
- Support full pipeline lifecycle management in your data platform. 