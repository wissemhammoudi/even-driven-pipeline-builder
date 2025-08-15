# Step Configuration Association Service

This module manages the associations between pipeline steps and step configurations, supporting flexible configuration and dynamic linking of steps to their configs.

---

## Main Class

### StepConfigurationAssociationService
Handles creation, retrieval, and deletion of associations between steps and step configurations.

**Key Methods:**
- `__init__(self)`: Initializes the association repository.
- `add_association(self, association_data)`: Creates a new association between a step and a step configuration.
- `get_steps_for_configuration(self, step_id)`: Returns all step IDs associated with a given configuration.
- `get_steps_ids_by_configuration_id(self, step_config_id)`: Returns all step IDs for a given step configuration.
- `delete_by_step_id(self, step_id)`: Deletes all associations for a given step ID.
- `rollback(self)`: Rolls back the current transaction in the repository.

---

Use this module to:
- Dynamically link steps to configurations in your pipelines.
- Support flexible and reusable step configuration management.
- Clean up or rollback associations as needed for data integrity. 