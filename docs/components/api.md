# Data Integration Component API

A RESTful API for managing data pipelines, users, steps, configurations, and schema change detection.

## Table of Contents
- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Root](#root)
  - [Pipelines](#pipelines)
  - [User](#user)
  - [Pipeline Steps](#pipeline-steps)
  - [Step Configuration](#step-configuration)
  - [Step Configuration Associations](#step-configuration-associations)
  - [Pipeline Runs](#pipeline-runs)
  - [Superset](#superset)
  - [Transformation](#transformation)
  - [User Pipeline Access](#user-pipeline-access)
  - [Dashboard](#dashboard)
  - [Pipeline Dashboard](#pipeline-dashboard)
- [Example Usage](#example-usage)

---

## Overview
This service provides a comprehensive API for:
- Creating and managing data pipelines
- Managing users and access control
- Configuring pipeline steps and associations
- Monitoring pipeline health and execution
- Integrating with Superset for visualization
- Agentic transformation capabilities

---

## API Endpoints

### Root
| Method | Path | Description |
|--------|------|-------------|
| GET    | `/`  | Health check endpoint. |

---

### Pipelines
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/pipeline/schema` | Get PostgreSQL schema info | `metadata_req` (body) |
| GET    | `/api/v1/pipeline/` | List pipelines | `user_id`, `offset`, `limit`, `deprecated`, `name`, `created_date` (query) |
| GET    | `/api/v1/pipeline/{pipeline_id}` | Get pipeline by ID | `pipeline_id` (path) |
| POST   | `/api/v1/pipeline/` | Create a new pipeline | `pipeline_data` (body) |
| DELETE | `/api/v1/pipeline/{pipeline_id}` | Delete a pipeline | `pipeline_id` (path) |
| PATCH  | `/api/v1/pipeline/` | Update a pipeline | `pipeline_data` (body) |
| GET    | `/api/v1/pipeline/{pipeline_id}/steps` | Get step IDs for a pipeline | `pipeline_id` (path) |
| GET    | `/api/v1/pipeline/{pipeline_id}/steps/details` | Get step details for a pipeline | `pipeline_id` (path) |
| PATCH  | `/api/v1/pipeline/steps` | Add a step to a pipeline | `step_data` (body) |
| DELETE | `/api/v1/pipeline/steps` | Delete steps from a pipeline | `step_data` (body) |

---

### User
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/users/signup` | User signup | `user_data` (body) |
| POST   | `/api/v1/users/login` | User login | `login_data` (body) |
| GET    | `/api/v1/users/` | List all users |  |
| GET    | `/api/v1/users/{username}` | Get user by username | `username` (path) |
| DELETE | `/api/v1/users/{user_id}` | Delete user | `user_id` (path) |
| PATCH  | `/api/v1/users/password` | Update user password | `password_data` (body) |
| PATCH  | `/api/v1/users/` | Update user info | `user_data` (body) |

---

### Pipeline Steps
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/steps/` | Create a step | `data` (body) |
| PATCH  | `/api/v1/steps/` | Update a step | `data` (body) |
| DELETE | `/api/v1/steps/{step_id}` | Delete a step | `step_id` (path) |
| GET    | `/api/v1/steps/step/{pipeline_id}` | List steps by pipeline | `pipeline_id` (path) |

---

### Step Configuration
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET    | `/api/v1/stepConfig/` | List all step configs |  |
| GET    | `/api/v1/stepConfig/types` | Get all step types |  |
| GET    | `/api/v1/stepConfig/tools` | Get tools per type | `type` (query) |
| GET    | `/api/v1/stepConfig/plugins` | Get plugins per tool and type | `tool`, `type` (query) |
| GET    | `/api/v1/stepConfig/toolsname` | Get all tool names |  |
| GET    | `/api/v1/stepConfig/configpertool` | Get step configs per tool | `tool` (query) |
| GET    | `/api/v1/stepConfig/configpertooltype` | Get step configs per tool, type, and plugin type | `tool`, `type`, `pluginType` (query) |
| PUT    | `/api/v1/stepConfig/{step_config_id}/deprecate` | Deprecate a step config | `step_config_id` (path) |

---

### Step Configuration Associations
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/step-config-associations/` | Create a step-config association | `association` (body) |
| GET    | `/api/v1/step-config-associations/step/{step_id}/configs` | Get configs for a step | `step_id` (path) |
| GET    | `/api/v1/step-config-associations/config/{step_config_id}/steps` | Get steps for a config | `step_config_id` (path) |

---

### Pipeline Runs
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET    | `/api/v1/pipeline-runs/pipeline/{pipeline_id}` | Get pipeline runs by pipeline ID | `pipeline_id` (path) |
| POST   | `/api/v1/pipeline-runs/start` | Start a pipeline run | `run` (body) |

---

### Superset
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/superset/visualization/start` | Start visualization for a pipeline | `control` (body) |

---

### Transformation
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| POST   | `/api/v1/transformation/create-transformation` | Create a transformation | `request` (body) |

---

### User Pipeline Access
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| PUT    | `/api/v1/user-pipeline-access/update` | Update user access to a pipeline | `access_data` (body), `user_id` (query) |
| POST   | `/api/v1/user-pipeline-access/bulk-grant` | Bulk grant access | `bulk_data` (body), `user_id` (query) |
| POST   | `/api/v1/user-pipeline-access/bulk-revoke` | Bulk revoke access | `bulk_data` (body), `user_id` (query) |
| GET    | `/api/v1/user-pipeline-access/pipeline/{pipeline_id}/users` | Get users for a pipeline | `pipeline_id`, `user_id` (path/query) |
| GET    | `/api/v1/user-pipeline-access/pipeline/{pipeline_id}/permissions/{user_id}` | Get user permissions for a pipeline | `pipeline_id`, `user_id` (path) |

---

### Dashboard
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET    | `/api/v1/dashboard/` | Get dashboard data for a user | `user_id` (query) |
| GET    | `/api/v1/dashboard/charts` | Get dashboard charts data for a user | `user_id`, `days` (query) |

---

### Pipeline Dashboard
| Method | Path | Description | Parameters |
|--------|------|-------------|------------|
| GET    | `/api/v1/pipeline-dashboard/pipeline/{pipeline_id}/analytics` | Get analytics for a pipeline | `pipeline_id`, `days` (query) |

---
