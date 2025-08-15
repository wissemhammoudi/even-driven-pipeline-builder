# Transformation Manager

The Transformation Manager handles agentic transformations and workflow automation for data pipeline steps.

---

## Overview

The Transformation Manager provides a comprehensive framework for managing data transformations, including N8N workflow automation, DBT transformations, SQLMesh operations, and custom transformation handlers.

---

## Components

### Base Handler
- **`base_handler.py`**: Abstract base class for all transformation handlers
- **`__init__.py`**: Package initialization file

### N8N Manager
- **`n8n_manager.py`**: Manages N8N workflow automation and execution

### DBT Handler
- **`dbt_handler.py`**: Handles DBT (Data Build Tool) transformations

### SQLMesh Handler
- **`sqlmesh_handler.py`**: Manages SQLMesh data modeling operations

### Database Utils
- **`database_utils.py`**: Database utility functions for transformations

---

## Architecture

### Handler Pattern
All transformation handlers inherit from `BaseHandler`, ensuring consistent interface and behavior across different transformation types.

### Workflow Integration
- **N8N Workflows**: Automated workflow execution
- **DBT Transformations**: SQL-based data transformations
- **SQLMesh Operations**: Data modeling and transformation
- **Custom Handlers**: Extensible transformation framework

---

## Usage

### Handler Registration
```python
# Register transformation handlers
handlers = {
    "n8n": N8NHandler(),
    "dbt": DBTHandler(),
    "sqlmesh": SQLMeshHandler()
}
```

### Transformation Execution
```python
# Execute transformation using appropriate handler
handler = handlers[transformation_type]
result = handler.execute(transformation_config)
```

---

## Dependencies

- **N8N**: Workflow automation platform
- **DBT**: Data transformation tool
- **SQLMesh**: Data modeling framework
- **Database Connectors**: Various database adapters

---

## Related Components

- **Pipeline Manager**: Overall pipeline orchestration
- **Transformation Agent**: Transformation request handling
- **API Endpoints**: Transformation API exposure
- **Pipeline Steps**: Transformation step execution
