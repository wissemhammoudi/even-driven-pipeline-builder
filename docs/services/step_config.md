# Step Configuration Service

This module manages step configuration objects, including listing, retrieving, and marking configurations as deprecated, as well as providing tools and plugin information for pipeline steps.

---

## Main Class

### configurationService
Handles all business logic related to step configurations, including CRUD operations, tool/plugin queries, and deprecation logic.

**Key Methods:**
- `__init__(self)`: Initializes repositories and related services.
- `list_step_config(self)`: Returns all step configurations.
- `get_by_id(self, step_config_id)`: Retrieves a step configuration by ID.
- `get_all_step_types(self)`: Returns all available step types.
- `get_all_step_tools_per_type(self, type)`: Returns all tools for a given step type.
- `get_all_step_plugins_type_per_tool_per_type(self, tool, type)`: Returns all plugin types for a given tool and step type.
- `get_all_step_config_per_type_per_tool_per_plugintype(self, tool, type, pluginType)`: Returns all step configs for a given tool, type, and plugin type.
- `get_all_tools_name(self)`: Returns all tool names.
- `get_step_config_per_tool(self, tool)`: Returns all step configs for a given tool.
- `mark_deprecated(self, step_config_id)`: Marks a step config (and related steps/pipelines) as deprecated.

---

Use this module to:
- Manage and query step configurations for pipelines.
- Support dynamic tool and plugin selection for pipeline steps.
- Handle deprecation and lifecycle management of step configs. 