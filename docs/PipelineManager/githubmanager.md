# Git Manager

The Git Manager handles all Git and GitHub operations for pipeline code management, including repository creation, code pushing, and code pulling.

---

## Overview

The `GitManager` class provides a high-level interface for managing Git repositories and GitHub operations within Docker containers. It handles repository creation, code versioning, and deployment workflows.

---

## Class: GitManager

### Initialization
```python
def __init__(self, docker_manager):
    self.docker_manager = docker_manager
```

**Dependencies:**
- `DockerManager` instance for container operations
- `GitHubConfig` for GitHub API configuration

---

## Key Methods

### Repository Management
- **`push_to_github(container_name, workdir)`**: Pushes code to GitHub repository
- **`pull_from_github(container_name)`**: Pulls code from GitHub repository

### Internal Operations
- **`_create_github_repository(repo_name, workdir)`**: Creates GitHub repository via API
- **`_initialize_and_push_git(repo_name, workdir)`**: Initializes Git and pushes code

---

## GitHub Integration

### Repository Creation
- Automatically creates private GitHub repositories
- Uses container name for repository naming convention
- Sets appropriate repository descriptions

### Authentication
- Uses GitHub token for API authentication
- Configures Git with user credentials
- Supports both username and email authentication

---

## Repository Naming Convention

The manager uses a specific naming convention for repositories:
- **Format**: `{container_prefix}_{container_id}`
- **Example**: `pipeline_1` for container `pipeline_step_1_123`

---
