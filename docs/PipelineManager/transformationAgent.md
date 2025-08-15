# Transformation Agent

The Transformation Agent handles transformation requests and orchestrates transformation workflows for data pipeline steps.

---

## Overview

The `transformationAgent` module provides functionality to send transformation requests and manage transformation workflows. It serves as a bridge between the pipeline execution framework and external transformation services.

---

## Function: send_transformation_request

### Function Signature
```python
def send_transformation_request(
    transformation: str,
    schema_name: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str
):
    # Implementation details
```

### Parameters
- **`transformation`**: Description of the transformation to perform
- **`schema_name`**: Database schema name
- **`db_host`**: Database host address
- **`db_port`**: Database port number
- **`db_name`**: Database name
- **`db_user`**: Database username
- **`db_password`**: Database password

---

## Functionality

### Transformation Request Handling
- **Request Processing**: Processes transformation requests from pipeline steps
- **Parameter Validation**: Validates transformation parameters
- **Service Integration**: Integrates with external transformation services
- **Response Handling**: Manages transformation service responses

---
