# Pipeline Step Service

This module manages the creation, update, deletion, and retrieval of pipeline steps, supporting step-level operations and associations within pipelines.

---

## Main Class

### StepService
Handles all business logic related to pipeline steps, including CRUD operations, deprecation, and association with pipelines.

**Key Methods:**
- `__init__(self)`: Initializes the step repository.
- `create_step(self, data)`: Creates a new step for a pipeline.
- `update_step(self, data)`: Updates an existing step's metadata and configuration.
- `delete_step(self, step_id)`: Soft-deletes a step by ID.
- `get_piplines_ids(self, step_ids)`: Returns pipeline IDs for a list of step IDs. 
- `mark_deprecated(self, step_ids)`: Marks steps as deprecated.
- `get_steps_by_pipeline(self, pipeline_id)`: Returns all steps for a given pipeline.
- `get_steps_id_by_pipeline(self, pipeline_id)`: Returns all step IDs for a given pipeline.
- `get_pipeline_id_by_step_id(self, step_id)`: Returns the pipeline ID for a given step ID.
- `rollback(self)`: Rolls back the current transaction in the repository.

---

Use this module to:
- Manage the lifecycle of steps within pipelines.
- Support step-level updates, deletions, and associations.
- Integrate with pipeline and configuration management for flexible data workflows. 