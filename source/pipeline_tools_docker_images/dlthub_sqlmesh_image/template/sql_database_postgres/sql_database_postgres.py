# flake8: noqa
from typing import Any
import json
import dlt
from dlt.sources.credentials import ConnectionStringCredentials
from dlt.sources.sql_database import sql_database
import sqlalchemy as sa


def load_select_tables_from_database(pipeline_name: str, target_schema: str, tables: list[str]) -> None:
    """Use the sql_database source to reflect an entire database schema and load select tables from it."""
    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination='postgres',
        dataset_name=target_schema
    )

    credentials = ConnectionStringCredentials()

    source = sql_database(credentials).with_resources(*tables)
    info = pipeline.run(source, write_disposition="replace")

    print(info)


if __name__ == "__main__":
    with open("./config/config.json", "r") as f:
        config = json.load(f)

    load_select_tables_from_database(
        pipeline_name=config["pipeline_name"],
        target_schema=config["target_schema"],
        tables=config["tables"]
    )
