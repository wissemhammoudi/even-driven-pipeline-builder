# Transformation Manager

The Transformation Manager provides a comprehensive framework for managing data transformations, including N8N workflow automation, DBT transformations, SQLMesh operations, and custom transformation handlers.

---

## Overview

The Transformation Manager system consists of several key components that work together to provide flexible, extensible data transformation capabilities. Each component has a specific role and can be extended or customized as needed.

---

## Core Components

### BaseHandler
The abstract base class that all transformation handlers must inherit from.

**Purpose**: Defines the common interface and behavior for all transformation handlers.

**Key Methods**:
- **`execute(transformation_config)`**: Abstract method that must be implemented by all handlers
- **`validate_config(config)`**: Validates the transformation configuration
- **`get_status()`**: Returns the current status of the transformation

**Usage**: All custom transformation handlers should inherit from this class to ensure consistency.

---

### TransformationManager
The main orchestrator class that manages all transformation operations.

**Purpose**: Coordinates transformation execution, manages handler registration, and provides a unified interface for transformation operations.

**Key Methods**:
- **`register_handler(handler_type, handler_instance)`**: Registers a new transformation handler
- **`execute_transformation(transformation_type, config)`**: Executes a transformation using the appropriate handler
- **`get_handler(transformation_type)`**: Retrieves a registered handler by type
- **`list_handlers()`**: Returns a list of all registered transformation handlers
- **`get_transformation_status(transformation_id)`**: Gets the status of a specific transformation

**Usage**: This is the main entry point for all transformation operations.

---

### N8NManager
Handles N8N workflow automation and execution.

**Purpose**: Manages N8N workflows, executes them, and monitors their status.

**Key Methods**:
- **`create_workflow(workflow_config)`**: Creates a new N8N workflow
- **`execute_workflow(workflow_id, input_data)`**: Executes an existing workflow with input data
- **`get_workflow_status(workflow_id)`**: Gets the current status of a workflow
- **`update_workflow(workflow_id, new_config)`**: Updates an existing workflow configuration
- **`delete_workflow(workflow_id)`**: Removes a workflow
- **`list_workflows()`**: Returns a list of all available workflows

**Usage**: Use this for workflow automation, data processing pipelines, and complex transformation logic.

---

### DBTHandler
Handles DBT (Data Build Tool) transformations.

**Purpose**: Manages DBT project execution, model compilation, and transformation runs.

**Key Methods**:
- **`run_models(model_names, target)`**: Runs specific DBT models
- **`compile_models(model_names)`**: Compiles DBT models without executing them
- **`test_models(model_names)`**: Runs tests on specified models
- **`get_model_status(model_name)`**: Gets the status of a specific model
- **`list_models()`**: Returns a list of all available models
- **`update_model_config(model_name, new_config)`**: Updates model configuration

**Usage**: Use this for SQL-based data transformations, data modeling, and data quality testing.

---

### SQLMeshHandler
Manages SQLMesh data modeling operations.

**Purpose**: Handles SQLMesh model execution, incremental processing, and schema evolution.

**Key Methods**:
- **`run_model(model_name, environment)`**: Runs a SQLMesh model in the specified environment
- **`plan_changes(environment)`**: Plans schema changes and model updates
- **`apply_changes(environment)`**: Applies planned changes to the environment
- **`get_model_versions(model_name)`**: Gets version history for a model
- **`rollback_model(model_name, version)`**: Rolls back a model to a specific version
- **`validate_model(model_name)`**: Validates model configuration and dependencies

**Usage**: Use this for advanced data modeling, incremental processing, and schema evolution management.

---

### DatabaseUtils
Provides utility functions for database operations.

**Purpose**: Common database operations and helper functions used by transformation handlers.

**Key Methods**:
- **`execute_query(query, connection_params)`**: Executes a SQL query
- **`get_table_schema(table_name, connection_params)`**: Gets schema information for a table
- **`validate_connection(connection_params)`**: Tests database connectivity
- **`get_table_size(table_name, connection_params)`**: Gets the size of a table
- **`backup_table(table_name, connection_params)`**: Creates a backup of a table

**Usage**: These utilities are used internally by other components for database operations.

---

## Transformation Types

### Workflow Transformations (N8N)
- **Data Processing**: Complex data transformation workflows
- **API Integration**: Connecting to external services and APIs
- **File Operations**: Processing files and documents
- **Scheduling**: Time-based transformation execution
- **Conditional Logic**: Decision-based transformation flows

### SQL Transformations (DBT)
- **Data Modeling**: Creating dimensional models and data marts
- **Data Quality**: Testing data integrity and consistency
- **Incremental Processing**: Processing only new or changed data
- **Documentation**: Auto-generating data documentation
- **Testing**: Comprehensive data testing and validation

### Data Modeling (SQLMesh)
- **Schema Evolution**: Managing changing data structures
- **Version Control**: Tracking model versions and changes
- **Environment Management**: Managing development, staging, and production
- **Incremental Processing**: Efficient data processing strategies
- **Rollback Capability**: Reverting to previous model versions

---

## Configuration

### Handler Registration
```python
# Register transformation handlers
transformation_manager.register_handler("n8n", N8NManager())
transformation_manager.register_handler("dbt", DBTHandler())
transformation_manager.register_handler("sqlmesh", SQLMeshHandler())
```

### Transformation Execution
```python
# Execute a transformation
result = transformation_manager.execute_transformation(
    transformation_type="dbt",
    config={
        "models": ["customer_dim", "order_fact"],
        "target": "production"
    }
)
```

---

## Error Handling

### Common Error Scenarios
- **Handler Not Found**: Transformation type not registered
- **Configuration Errors**: Invalid transformation configuration
- **Execution Failures**: Transformation execution errors
- **Resource Issues**: Insufficient resources or permissions

### Error Response Format
```json
{
    "success": false,
    "error": "Transformation failed",
    "details": "Specific error message",
    "transformation_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## Best Practices

1. **Handler Registration**: Always register handlers before using them
2. **Configuration Validation**: Validate configurations before execution
3. **Error Handling**: Implement proper error handling for all transformations
4. **Resource Management**: Monitor and manage resource usage
5. **Logging**: Maintain comprehensive logs for debugging and monitoring

---

## Related Components

- **Pipeline Manager**: Overall pipeline orchestration
- **Transformation Agent**: Transformation request handling
- **API Endpoints**: Transformation API exposure
- **Pipeline Steps**: Transformation step execution
