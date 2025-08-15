# Meltano Runner

The Meltano Runner handles Meltano-based data integration and transformation steps within the pipeline execution framework.

---

## What is Meltano?

Meltano is an open-source platform for building, running, and managing data pipelines. It provides:

- **Data Extraction**: Singer-based data extraction
- **Data Loading**: Flexible data loading capabilities
- **Data Transformation**: Built-in transformation tools
- **Pipeline Orchestration**: Workflow management

### Supported Operations
- Data extraction from various sources
- Data transformation and processing
- Data loading to target systems
- Pipeline configuration and management

---

## Implementation

### Class: MeltanoRunner

The `MeltanoRunner` class implements the `BaseStepRunner` interface to provide Meltano-specific pipeline step execution.

### Methods

#### `__init__(self)`
- **Purpose**: Initializes the Meltano runner instance
- **What it does**: Sets up container and docker_manager attributes to None initially
- **When called**: Automatically called when creating a new MeltanoRunner instance
- **Parameters**: None
- **Returns**: None

#### `config(step, name)`
- **Purpose**: Configures the Meltano step based on step type (data ingestion or transformation)
- **What it does**:
  - Determines the step type from configuration
  - Routes to appropriate configuration method based on type
  - Calls either `_configure_data_ingestion` or `_configure_data_transformation`
- **Parameters**: 
  - `step`: Dictionary containing step configuration
  - `name`: Name identifier for the step
- **Returns**: None
- **Error handling**: Raises RuntimeError if Docker manager is not initialized or configuration fails

#### `_configure_data_ingestion(step, container_name, workdir)`
- **Purpose**: Private method to configure data ingestion steps
- **What it does**:
  - Initializes Meltano project if directory doesn't exist
  - Adds extractor plugin with connection configuration
  - Adds loader plugin with connection configuration
  - Configures table and column selection for data extraction
- **Parameters**: 
  - `step`: Step configuration dictionary
  - `container_name`: Name of the container
  - `workdir`: Working directory path
- **Returns**: None
- **Usage**: Called internally by the `config` method

#### `_configure_data_transformation(step, container_name, workdir)`
- **Purpose**: Private method to configure data transformation steps
- **What it does**:
  - Initializes Meltano project if directory doesn't exist
  - Adds utility plugin (like dbt) with database configuration
  - Sets up transformation directory structure
  - Configures table synchronization for transformations
- **Parameters**: 
  - `step`: Step configuration dictionary
  - `container_name`: Name of the container
  - `workdir`: Working directory path
- **Returns**: None
- **Usage**: Called internally by the `config` method

#### `start(step, name)`
- **Purpose**: Starts the Meltano step execution
- **What it does**:
  - For data ingestion: Sets passwords and runs extractor-loader pipeline
  - For data transformation: Sets password and runs dbt transformations
- **Parameters**: 
  - `step`: Dictionary containing step configuration
  - `name`: Name identifier for the step
- **Returns**: None
- **Error handling**: Raises RuntimeError if Docker manager is not initialized or execution fails

