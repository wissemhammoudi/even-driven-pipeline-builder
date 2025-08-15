# Source Tables Metadata

The Source Tables Metadata service provides PostgreSQL schema information and metadata extraction capabilities for pipeline configuration and data source management.

---

## Overview

The `PostgreSQLSourceMetadata` class provides functionality to extract and analyze PostgreSQL database schemas, including table structures, column information, and metadata that can be used for pipeline configuration and data source setup.

---

## Class: PostgreSQLSourceMetadata

### Initialization
```python
def __init__(self, host: str, dbname: str, user: str, password: str, port: int):
    self.host = host
    self.dbname = dbname
    self.user = user
    self.password = password
    self.port = port
```

### Key Methods
- **`get_schema_info(schema_name)`**: Retrieves schema information for the specified schema

---

## Functionality

### Schema Information Extraction
- **Table Discovery**: Automatically discovers all tables in a schema
- **Column Analysis**: Extracts column names, types, and constraints
- **Index Information**: Retrieves index details for performance optimization
- **Constraint Details**: Extracts primary key, foreign key, and unique constraints

### Metadata Analysis
- **Data Type Mapping**: Maps PostgreSQL types to pipeline-compatible formats
- **Schema Validation**: Validates schema structure for pipeline compatibility
- **Size Estimation**: Provides table size and row count estimates

---
