# Configuration Guide

This guide covers all configuration options for the Near Real-time Data Pipeline project, including environment variables, Docker settings, and service configurations.

---

##  Quick Start Configuration

### **Environment File (.env)**
Create a `.env` file in the project root with the following configuration:

```bash
# PostgreSQL Configuration
DB_HOST=postgres
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=mydatabase

# JWT Authentication
secret_key=your_secret_key
algorithm=HS256
token_expiry_minutes=30
version=V1

# GitHub Integration (Optional)
github_token=your_github_token
github_username=your_username
github_email=your_email

# Docker Engine
meltano_docker_image=wissem020/meltano
dlt_sqlmesh_superset_docker_image=wissem020/sqlmesh_dlt_superset
Docker_Client_Base_Url=unix://var/run/docker.sock

# Apache Superset
superset_secret_key=your_superset_secret_key
superset_user=admin
superset_password=admin123
superset_sqlalchemy_uri=postgresql://user:password@postgres:5432/postgres
superset_url=http://superset:8088
superset_user_url=http://localhost:8088

# API and Frontend
api_prefix=/api/v1
base_url=/api/v1
frontend_url=http://frontend:3000
frontend_url_develop=http://localhost:3000

# External Services
transformation_agent_Url=http://n8n:5678/webhook/sql-transformation
```

---

## Core Database Settings

### **PostgreSQL Configuration**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database host address | `postgres` | Yes |
| `DB_PORT` | Database port number | `5432` | Yes |
| `DB_USER` | Database username | `user` | Yes |
| `DB_PASSWORD` | Database password | `password` | Yes |
| `DB_NAME` | Database name | `mydatabase` | Yes |

---

## Security Configuration

### **JWT Authentication**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `secret_key` | JWT signing secret | - | Yes |
| `algorithm` | JWT algorithm | `HS256` | No |
| `token_expiry_minutes` | Token expiration time | `30` | No |
| `version` | API version | `V1` | No |

### **Security Best Practices**
- Use strong, unique secret keys
- Rotate keys regularly in production
- Store secrets securely (not in version control)
- Use HTTPS in production environments

---

## Docker Configuration

### **Docker Images**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `meltano_docker_image` | Meltano container image | `wissem020/meltano` | Yes |
| `dlt_sqlmesh_superset_docker_image` | DLT/SQLMesh/Superset image | `wissem020/sqlmesh_dlt_superset` | Yes |
| `Docker_Client_Base_Url` | Docker daemon URL | `unix://var/run/docker.sock` | Yes |

### **Docker Requirements**
- **Docker**: 20.10+ version
- **Docker Compose**: 2.0+ version
- **Docker Engine**: Running and accessible

---

## GitHub Integration

### **GitHub Configuration**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `github_token` | Personal access token | - | No |
| `github_username` | GitHub username | - | No |
| `github_email` | GitHub email address | - | No |


## Apache Superset Configuration

### **Superset Settings**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `superset_secret_key` | Superset secret key | - | Yes |
| `superset_user` | Admin username | `admin` | No |
| `superset_password` | Admin password | `admin123` | No |
| `superset_sqlalchemy_uri` | Database connection string | - | Yes |
| `superset_url` | Internal Superset URL | `http://superset:8088` | Yes |
| `superset_user_url` | External Superset URL | `http://localhost:8088` | Yes |


## API and Frontend Configuration

### **URL Configuration**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `api_prefix` | API endpoint prefix | `/api/v1` | No |
| `base_url` | Base API URL | `/api/v1` | No |
| `frontend_url` | Frontend container URL | `http://frontend:3000` | Yes |
| `frontend_url_develop` | Local development URL | `http://localhost:3000` | No |

### **API Configuration**
- **Versioning**: API version control via prefix
- **CORS**: Configured for frontend access
- **Rate Limiting**: Implemented for production use

---

## External Services

### **Transformation Service**
| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `transformation_agent_Url` | N8N webhook URL | `http://n8n:5678/webhook/sql-transformation` | Yes |
