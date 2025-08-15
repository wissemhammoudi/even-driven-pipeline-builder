# Docker Manager

The Docker Manager handles all Docker container operations for pipeline execution, including container creation, management, and cleanup.

---

## Overview

The `DockerManager` class provides a high-level interface for managing Docker containers used in pipeline execution. It handles container lifecycle, network configuration, and command execution within containers.

---

## Class: DockerManager

### Initialization
```python
def __init__(self):
    self.client = docker.DockerClient(base_url=DockerConfig.Docker_Client_Base_Url)
    self.container = None
```

**Dependencies:**
- `docker` library for Docker operations
- `DockerConfig` for configuration settings

---

## Key Methods

### Container Creation
- **`create_container(name, image, port)`**: Creates and starts a Docker container
- **`_create_container_config(name, image, port)`**: Generates container configuration

### Container Management
- **`stop_container()`**: Stops and removes the current container
- **`_wait_for_container(timeout)`**: Waits for container to be ready

### Command Execution
- **`exec_command(command, retries, workdir, run_in_background)`**: Executes commands within the container

---

## Container Configuration

### Default Settings
- **Memory Limit**: 4GB
- **Working Directory**: `/project`
- **Entry Point**: `sh -c`
- **Default Command**: `sleep infinity`
- **Detached Mode**: Enabled
- **Interactive Mode**: Enabled (stdin_open, tty)

### Port Configuration
- **Default**: No port mapping
- **Optional**: 8088/tcp port mapping when specified

---

## Network Configuration

- Automatically connects containers to the `near-realtime-data-pipeline_default` network
- Enables inter-container communication
- Supports custom network configurations

---
