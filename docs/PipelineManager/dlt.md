# DLT Runner

The DLT (Data Load Tool) Runner handles DLT-based data loading and transformation steps within the pipeline execution framework.

---

## What is DLT?

DLT (Data Load Tool) is an open-source Python library for data loading and transformation. It provides:

- **Data Loading**: Efficient data loading to various destinations
- **Data Transformation**: Built-in transformation capabilities  
- **Schema Evolution**: Automatic schema handling
- **Incremental Processing**: Support for incremental data updates

### Supported Operations
- Data extraction from various sources
- Data transformation and processing
- Data loading to target systems
- Schema management and evolution
- Incremental data processing

---

## Implementation

### Class: DltRunner

The `DltRunner` class implements the `BaseStepRunner` interface to provide DLT-specific pipeline step execution.

### Methods

#### `__init__(self)`
- **Purpose**: Initializes the DLT runner instance
- **What it does**: Sets up container and docker_manager attributes to None initially
- **When called**: Automatically called when creating a new DltRunner instance
- **Parameters**: None
- **Returns**: None

#### `config(step, name)`
- **Purpose**: Configures the DLT pipeline step with the given parameters
- **What it does**: 
  - Creates working directory for the container
  - Initializes DLT project with source and destination
  - Sets up connection credentials in secrets.toml file
  - Configures the DLT pipeline environment
- **Parameters**: 
  - `step`: Dictionary containing step configuration
  - `name`: Name identifier for the step
- **Returns**: None
- **Error handling**: Raises RuntimeError if Docker manager is not initialized or configuration fails

#### `start(step, name)`
- **Purpose**: Starts the DLT pipeline execution
- **What it does**:
  - Creates Python virtual environment using uv
  - Installs required dependencies from requirements.txt
  - Executes the generated Python script for the pipeline
- **Parameters**: 
  - `step`: Dictionary containing step configuration
  - `name`: Name identifier for the step
- **Returns**: None
- **Error handling**: Raises RuntimeError if Docker manager is not initialized or execution fails

