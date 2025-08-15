# Pipeline Manager Service

The Pipeline Manager is a comprehensive orchestration service that manages the creation, execution, and lifecycle of data pipelines. It integrates Docker containers, GitHub repositories, and various data transformation tools to provide a unified pipeline management experience.

---

## Overview

The Pipeline Manager service provides:
- **Unified Pipeline Orchestration**: Manages multiple pipeline steps with different tools
- **Docker Container Management**: Handles container lifecycle for pipeline execution
- **GitHub Integration**: Manages code repositories for pipeline steps
- **Multi-Tool Support**: Integrates with Meltano, DLT, SQLMesh, and Superset
- **Transformation Management**: Handles agentic transformations and workflow automation

---

## Core Classes

### PipelineManager
The main orchestrator class that manages the entire pipeline lifecycle.

**Key Methods:**
- `__init__(self)`: Initializes Docker manager, Git manager, and step tracking
- `add_step(step_name, runner, stepconfig, isvisual)`: Adds a step to the pipeline
- `delete_step(step_name)`: Removes a step from the pipeline
- `get_runner(tool)`: Returns appropriate runner for the specified tool
- `get_image(tool)`: Returns Docker image for the specified tool
- `get_steps()`: Returns all pipeline steps
- `get_visualization_step()`: Returns the visualization step name if exists
- `create_pipeline()`: Creates pipeline with port exposure and GitHub integration
- `run_pipeline()`: Executes the pipeline and all its steps
- `cleanup()`: Cleans up resources and containers

**Tool Support:**
- **Meltano**: Data integration and transformation
- **DLT**: Data loading and transformation
- **SQLMesh**: Data modeling and transformation
- **Superset**: Data visualization and dashboards

---

## Step Runners

### BaseStepRunner (Interface)
Abstract base class that defines the interface for all step runners.

**Abstract Methods:**
- `config(step_config, workdir, retries)`: Configure the step with given parameters

### MeltanoRunner
Handles Meltano-based data integration and transformation steps.

**Documentation**: [Meltano Runner](meltano.md)

### DltRunner
Manages DLT (Data Load Tool) operations for data loading and transformation.

**Documentation**: [DLT Runner](dlt.md)

### SqlmeshRunner
Handles SQLMesh operations for data modeling and transformation.

**Documentation**: [SQLMesh Runner](sqlmesh.md)

### SupersetRunner
Manages Superset dashboard creation and configuration.

**Documentation**: [Superset Runner](superset.md)

---

## Management Components

### DockerManager
Handles Docker container lifecycle and operations.

**Key Features:**
- Container creation and management
- Port mapping and network configuration
- Resource cleanup and monitoring

**Documentation**: [Docker Manager](dockermanager.md)

### GitManager
Manages GitHub repository operations for pipeline code.

**Key Features:**
- Code push to GitHub repositories
- Code pull from GitHub repositories
- Repository management and organization

**Documentation**: [Git Manager](githubmanager.md)

### TransformationManager
Handles agentic transformations and workflow automation.

**Components:**
- **BaseHandler**: Abstract base for transformation handlers
- **N8N Manager**: Manages N8N workflow automation
- **DBT Handler**: Handles DBT transformations
- **SQLMesh Handler**: Manages SQLMesh transformations

**Documentation**: [Transformation Manager](transfomrationManager/README.md)

---

## Additional Utilities

### SourceTablesMetadata
Provides PostgreSQL schema information and metadata extraction.

**Documentation**: [Source Tables Metadata](sourceTablesMetadata.md)

### SQLStringValidator
Validates SQL strings and ensures proper syntax.

**Documentation**: [SQL String Validator](sql_string_validator.md)

### TransformationAgent
Handles transformation requests and orchestrates transformation workflows.

**Documentation**: [Transformation Agent](transformationAgent.md)

---

## Component Documentation

For detailed information about each component, refer to the individual documentation files:

- [Docker Manager](dockermanager.md)
- [Git Manager](githubmanager.md)
- [Meltano Runner](meltano.md)
- [DLT Runner](dlt.md)
- [SQLMesh Runner](sqlmesh.md)
- [Superset Runner](superset.md)
- [Source Tables Metadata](sourceTablesMetadata.md)
- [SQL String Validator](sql_string_validator.md)
- [Transformation Agent](transformationAgent.md)
- [Transformation Manager](transfomrationManager/README.md)
