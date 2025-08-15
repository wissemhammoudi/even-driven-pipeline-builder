# Pipeline Run Service

This module manages the execution and tracking of pipeline runs, including starting pipelines, handling errors, and recording run metadata.

---

## Main Class

### PipelineRunService
Handles the orchestration and tracking of pipeline runs, including error handling and status updates.

**Key Methods:**
- `__init__(self)`: Initializes the repository, step service, and pipeline service.
- `get_pipeline_runs_by_pipeline_id(self, pipeline_id)`: Retrieves all runs for a given pipeline.
- `start_pipeline(self, run)`: Starts a pipeline run, executes all steps, handles errors, and records run metadata and status.

---

Use this module to:
- Start and track the execution of data pipelines.
- Record run status, errors, and timing information.
- Integrate with pipeline and step management for end-to-end orchestration. 