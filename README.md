# Near Real-time Data Pipeline

A comprehensive data pipeline management platform that enables near real-time data ingestion, transformation, and visualization.

##  Key Features

- **Visual Pipeline Management** - Create and configure data pipelines through an intuitive interface
- **Multi-Source Data Ingestion** - Real-time ingestion from PostgreSQL
- **Advanced Data Transformation** - Powered by multiple transformation types
- **Interactive Dashboards** - Built-in Apache Superset integration for data visualization
- **Security** - Role-based access control and secure authentication
- **Monitoring** - Live pipeline metrics and execution status tracking

## Prerequisites

Ensure you have the following installed on your system:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.30+)
- **Node.js** (18.0+) - for local development
- **Python** (3.9+) - for local development

##  Quick Start

### Step 1: Clone and Setup

```bash
git clone https://github.com/elyadata/near-realtime-data-pipeline.git
cd near-realtime-data-pipeline
```

### Step 2: Launch Services

```bash
docker-compose up -d
```

This command starts all required services in the background.

### Step 3: Verify Deployment

##  Service Access Points

| Service | URL | Default Credentials | Purpose |
|---------|-----|-------------------|---------|
| **Main Application** | http://localhost:3000 | Register new account | Primary user interface |
| **API Documentation** | http://localhost:8010/docs | None required | Interactive API docs |
| **Database Admin** | http://localhost:5050 | `admin@admin.com` / `admin` | PostgreSQL management |
| **Apache Superset** | http://localhost:8088 | `admin` / `admin123` | Data visualization |
| **N8N Workflows** | http://localhost:5678 | Register new account | Workflow automation |

## Core Database Settings

```bash
# PostgreSQL Configuration
DB_HOST=postgres
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=mydatabase
```

### Security Configuration

```bash
# JWT Authentication
secret_key=your_secret_key
algorithm=HS256
token_expiry_minutes=30
version=V1
```

### Integration Settings

```bash
# GitHub Integration (Optional)
github_token=your_github_token
github_username=your_username
github_email=your_email

# Docker Engine
meltano_docker_image=wissem020/meltano
dlt_sqlmesh_superset_docker_image=wissem020/sqlmesh_dlt_superset
Docker_Client_Base_Url=unix://var/run/docker.sock
```

### Apache Superset Configuration

```bash
# Superset Settings
superset_secret_key=your_superset_secret_key
superset_user=admin
superset_password=admin123
superset_sqlalchemy_uri=postgresql://user:password@postgres:5432/postgres
superset_url=http://superset:8088
superset_user_url=http://localhost:8088
```

### API and Frontend Settings

```bash
# Application URLs
api_prefix=/api/v1
base_url=/api/v1
frontend_url=http://frontend:3000
frontend_url_develop=http://localhost:3000

# External Services
transformation_agent_Url=http://n8n:5678/webhook/sql-transformation
```

##  Architecture Overview

The platform consists of several interconnected services:

- **Frontend** - React-based user interface
- **Backend API** - FastAPI-powered REST API
- **PostgreSQL** - Primary data storage
- **Apache Superset** - Business intelligence and visualization
- **N8N** - Workflow automation and data transformation
- **PgAdmin** - Database administration interface

## Documentation

### **📚 Comprehensive Documentation**
- **[Documentation Index](docs/README.md)** - Complete project documentation organized by service and component
- **[API Reference](docs/components/api.md)** - Complete API endpoint documentation
- **[Configuration Guide](docs/components/configuration.md)** - Environment setup and configuration

### **🔧 Service Documentation**

#### **Core Services**
- **API Service** - [Complete API Reference](docs/components/api.md)
- **User Service** - [User Management](docs/services/user.md)
- **Authentication Service** - [Security & JWT Management](docs/services/authentication.md)
- **Pipeline Service** - [Pipeline Management](docs/services/pipeline.md)
- **Pipeline Steps** - [Step Configuration](docs/services/pipeline_step.md)
- **Pipeline Runs** - [Execution Monitoring](docs/services/pipeline_run.md)
- **Step Configuration** - [Configuration Management](docs/services/step_config.md)

#### **Dashboard & Visualization**
- **Dashboard Service** - [Dashboard Management](docs/services/dashboard.md)
- **Pipeline Dashboard Association** - [Pipeline-Dashboard Linking](docs/services/pipeline_dashboard.md)
- **Dashboard Pipeline Association** - [Dashboard-Pipeline Linking](docs/services/dashboard_pipeline_association.md)

#### **Access Control & Associations**
- **User Pipeline Access** - [Access Management](docs/services/user_pipeline_access.md)
- **User Superset Account Association** - [Superset Integration](docs/services/user_superset_account_association.md)
- **Step Configuration Association** - [Step-Config Linking](docs/services/step_configuration_association.md)

#### **Pipeline Orchestration**
- **Pipeline Manager** - [Pipeline Orchestration & Execution](docs/PipelineManager/README.md)

### **Pipeline Tools**
- **N8N Workflow Guide** - [Setup Instructions](source/pipeline_tools_docker_images/n8n_image/n8nTemplate/readme.md)
- **Docker Images** - Custom images for pipeline tools:
  - [N8N Image](source/pipeline_tools_docker_images/n8n_image/)
  - [Superset Image](source/pipeline_tools_docker_images/superset_image/)
  - [Meltano Image](source/pipeline_tools_docker_images/meltano_image/)
  - [DLT/SQLMesh Image](source/pipeline_tools_docker_images/dlthub_sqlmesh_image/)

### **Database & Initialization**
- **Source Database Setup** - [Initialization Guide](source/init_database/init_source_database/readme.md)
- **Configuration Tables** - [Database Schema](source/init_database/init_configuration_table/)

## Configuration Files

The platform uses several configuration files for different components:

- **Main Config**: [`source/config/config.py`](source/config/config.py) - Core application settings
- **N8N Templates**: [`source/pipeline_tools_docker_images/n8n_image/n8nTemplate/`](source/pipeline_tools_docker_images/n8n_image/n8nTemplate/) - Workflow templates
- **Docker Images**: [`source/pipeline_tools_docker_images/`](source/pipeline_tools_docker_images/) - Custom service images
- **Database Init**: [`source/init_database/`](source/init_database/) - Database initialization scripts

## Project Structure

```
even-driven-pipeline-builder/
├── source/                           # Backend source code
│   ├── api/                         # API endpoints and documentation
│   ├── config/                      # Configuration management
│   ├── models/                      # Data models and database schemas
│   ├── schema/                      # Pydantic schemas for validation
│   ├── repository/                  # Data access layer
│   ├── service/                     # Business logic services
│   │   ├── user/                   # User management
│   │   ├── authentication/          # Security & JWT
│   │   ├── pipeline/               # Pipeline management
│   │   ├── pipeline_step/          # Step configuration
│   │   ├── pipeline_run/           # Execution monitoring
│   │   ├── dashboard/              # Dashboard management
│   │   ├── step_config/            # Configuration management
│   │   ├── user_pipeline_access/   # Access control
│   │   ├── user_superset_account_association/ # Superset integration
│   │   ├── step_configuration_association/ # Step-config linking
│   │   ├── pipeline_dashboard/     # Pipeline-dashboard linking
│   │   ├── dashboard_pipeline_association/ # Dashboard-pipeline linking
│   │   └── PipelineManager/        # Pipeline orchestration
│   ├── exceptions/                  # Custom exception handling
│   ├── pipeline_tools_docker_images/ # Custom Docker images
│   └── init_database/              # Database initialization
├── frontendreact/                   # React frontend application
├── n8n/                            # N8N workflow configurations
├── docker-compose.yaml             # Service orchestration
└── README.md                       # This file
```
