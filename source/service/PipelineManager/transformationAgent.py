import requests
from source.config.config import ExternalServicesConfig
import json

def send_transformation_request(transformation, schema_name="", db_host="", db_port=5432, db_name="", db_user="", db_password=""):
    url = ExternalServicesConfig.transformation_agent_Url
    payload = {
        "transformation": transformation,
        "schema_name": schema_name,
        "db_host": db_host,
        "db_port": db_port,
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password,
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
