# Superset Runner

The Superset Runner handles Apache Superset dashboard creation and configuration steps within the pipeline execution framework.

---

## What is Apache Superset?

Apache Superset is a modern, enterprise-ready business intelligence web application that provides:

- **Data Visualization**: Rich interactive dashboards
- **SQL Editor**: Advanced SQL query interface
- **Chart Library**: Extensive chart and visualization options
- **Security**: Role-based access control
- **API Support**: RESTful API for automation

### Supported Operations
- Dashboard creation and configuration
- Chart and visualization setup
- User and role management
- Data source configuration
- Dashboard sharing and permissions

---

## Implementation

### Class: SupersetRunner

The `SupersetRunner` class implements the `BaseStepRunner` interface to provide Superset-specific pipeline step execution.

### Methods

#### `__init__(self)`
- **Purpose**: Initializes the Superset runner instance
- **What it does**: Sets up container, docker_manager, visualization_container, client, username, and password attributes to None initially
- **When called**: Automatically called when creating a new SupersetRunner instance
- **Parameters**: None
- **Returns**: None

#### `_initialize_superset_client(username, password)`
- **Purpose**: Private method to initialize and authenticate Superset client
- **What it does**:
  - Creates SupersetClient instance with provided credentials
  - Attempts to authenticate with Superset
  - Raises error if authentication fails
- **Parameters**: 
  - `username`: Username for Superset authentication
  - `password`: Password for Superset authentication
- **Returns**: None
- **Error handling**: Raises RuntimeError if authentication fails
- **Usage**: Called internally by the `config` method

#### `config(step, name)`
- **Purpose**: Configures Superset step and creates dashboard
- **What it does**:
  - Initializes Superset client with admin credentials
  - Creates database connection if it doesn't exist
  - Creates a new dashboard with proper permissions
  - Returns the created dashboard ID
- **Parameters**: 
  - `step`: Dictionary containing step configuration
  - `name`: Name identifier for the step
- **Returns**: Integer dashboard ID
- **Error handling**: Raises RuntimeError if Docker manager is not initialized, database creation fails, or dashboard creation fails

