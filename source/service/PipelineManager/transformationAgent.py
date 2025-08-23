import httpx
from source.config.config import external_services_config
import json

async def send_transformation_request(transformation_data: dict):
    url = external_services_config.n8n_webhook_Url
    payload = {
        "transformation": transformation_data,
        "schema_name": transformation_data.get("schema_name", ""),
        "db_host": transformation_data.get("db_host", ""),
        "db_port": transformation_data.get("db_port", 5432),
        "db_name": transformation_data.get("db_name", ""),
        "db_user": transformation_data.get("db_user", ""),
        "db_password": transformation_data.get("db_password", ""),
    }
    headers = {
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    return response.json()
