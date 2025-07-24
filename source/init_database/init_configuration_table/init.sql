CREATE TABLE IF NOT EXISTS configurations (
    step_config_id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    tool VARCHAR(255) NOT NULL,
    plugin_type VARCHAR(255) NOT NULL,
    plugin_name VARCHAR(255) NOT NULL,
    schema_change_tool VARCHAR(255) DEFAULT NULL,
    is_deprecated BOOLEAN NOT NULL DEFAULT FALSE,
    config JSONB
);
INSERT INTO configurations (type, tool, plugin_type, plugin_name, schema_change_tool, is_deprecated, config)
VALUES 
('data ingestion', 'meltano', 'loader', 'target-mongodb', 'mongodb', FALSE, '{
    "connection_string": "mongodb://${MONGO_USERNAME}:${MONGO_PASSWORD}@mongodb0.example.com:PORT",
    "db_name": "Name of the target db inside your mongoDB"
}'),
('data ingestion', 'dlt', 'source', 'sql_database', 'postgres', FALSE, '{
    "drivername": "Database driver, e.g., postgresql+psycopg2",
    "database": "Name of the source database",
    "password": "Password to connect to the source database",
    "username": "Username for authentication",
    "host": "Hostname or IP of the source database",
    "port": "Port number for the source database"
}'),
('data ingestion', 'dlt', 'destination', 'postgres', 'postgres', FALSE, '{
    "database": "Name of the destination database",
    "password": "Password to connect to the destination database",
    "username": "Username for authentication",
    "host": "Hostname or IP of the destination database",
    "port": "Port number for the destination database"
}'),
('data ingestion', 'meltano', 'loader', 'target-postgres', 'postgres', FALSE, '{
    "database": "Database name.",
    "host": "Hostname for postgres instance.",
    "password": "Password used to authenticate.",
    "port": "The port on which postgres is awaiting connections.",
    "user": "User name used to authenticate.",
    "sqlalchemy_url": "sqlalchemy url",
    "default_target_schema": "Postgres schema to send data to"
}'),
('data ingestion', 'meltano', 'extractor', 'tap-postgres', 'postgres', FALSE, '{
    "database": "Database name. Note if sqlalchemy_url is set this will be ignored.",
    "filter_schemas": "If an array of schema names is provided, the tap will only process the specified Postgres schemas and ignore others. If left blank, the tap automatically determines ALL available Postgres schemas.",
    "host": "Hostname for postgres instance. Note if sqlalchemy_url is set this will be ignored.",
    "password": "Password used to authenticate. Note if sqlalchemy_url is set this will be ignored.",
    "port": "The port on which postgres is awaiting connection. Note if sqlalchemy_url is set this will be ignored.",
    "user": "User name used to authenticate.",
    "sqlalchemy_url": "sqlalchemy url"
}'),
('data ingestion', 'meltano', 'extractor', 'tap-mongodb', 'mongodb', FALSE, '{
    "database_excludes": "A list of databases to exclude. If this list is empty, no databases will be excluded.",
    "database_includes": "A list of databases to include. If this list is empty, all databases will be included.",
    "infer_schema_max_docs": "The maximum number of documents to sample when inferring the schema. This is only used when infer_schema is true.",
    "Mongo": "These props are passed directly to pymongo MongoClient allowing the tap user full flexibility not provided in other Mongo taps since every kwarg can be tuned.",
    "mongo_file_location": "Optional file path, useful if reading mongo configuration from a file.",
    "optional_replication_key": "This setting allows the tap to continue processing if a document is missing the replication key. Useful if a very small percentage of documents are missing the property.",
    "strategy": "The strategy to use for schema resolution. Defaults to ''raw''. The ''raw'' strategy uses a relaxed schema using additionalProperties: true to accept the document as-is leaving the target to respect it. Useful for blob or jsonl. The ''envelope'' strategy will envelope the document under a key named document. The target should use a variant type for this key. The ''infer'' strategy will infer the schema from the data based on a configurable number of documents.",
    "stream_prefix": "Optionally add a prefix for all streams, useful if ingesting from multiple shards/clusters via independent tap-mongodb configs. This is applied during catalog generation. Regenerate the catalog to apply a new stream prefix."
}'),
('data transformation', 'meltano', 'utility', 'dbt-postgres', NULL, FALSE, '{
    "dbname": "The db to connect to.",
    "host": "The postgres host to connect to.",
    "password": "The password to connect with.",
    "port": "The port to connect to.",
    "schema": "Specifies the schema in your Postgres database where dbt will create and manage tables.",
    "user": "The PostgreSQL user that dbt should use to connect to the database.",
    "transformation": [{
        "null_value": {
            "sum": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "avg": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "min": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "max": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "count": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "median": ["integer", "bigint", "smallint", "numeric", "real", "double precision"]
        },
        "string_transform": {
            "upper": ["varchar", "text", "char"],
            "lower": ["varchar", "text", "char"]
        },
        "date_transform": {
            "extract_year": ["date", "timestamp"],
            "extract_month": ["date", "timestamp"],
            "extract_day": ["date", "timestamp"]
        },
        "lookup_join": {
            "left_join": ["column"],
            "right_join": ["column"],
            "inner_join": ["column"],
            "full_outer_join": ["column"],
            "cross_join": ["column"]
        }
    }]
}'),
('data transformation', 'sqlmesh', 'utility', 'postgres', NULL, FALSE, '{
    "database": "The db to connect to.",
    "host": "The postgres host to connect to.",
    "password": "The password to connect with.",
    "port": "The port to connect to.",
    "schema": "Specifies the schema in your Postgres database where dbt will create and manage tables.",
    "user": "The PostgreSQL user that dbt should use to connect to the database.",
    "transformation": [{
        "null_value": {
            "sum": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "avg": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "min": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "max": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "count": ["integer", "bigint", "smallint", "numeric", "real", "double precision"],
            "median": ["integer", "bigint", "smallint", "numeric", "real", "double precision"]
        },
        "string_transform": {
            "upper": ["varchar", "text", "char"],
            "lower": ["varchar", "text", "char"]
        },
        "date_transform": {
            "extract_year": ["date", "timestamp"],
            "extract_month": ["date", "timestamp"],
            "extract_day": ["date", "timestamp"]
        },
        "lookup_join": {
            "left_join": ["column"],
            "right_join": ["column"],
            "inner_join": ["column"],
            "full_outer_join": ["column"],
            "cross_join": ["column"]
        }
    }]
}'),
('data visualization', 'superset', 'utility', 'superset:postgres', NULL, FALSE, '{
    "SQLALCHEMY_DATABASE_URI": "Superset metadata database connection string."
}');