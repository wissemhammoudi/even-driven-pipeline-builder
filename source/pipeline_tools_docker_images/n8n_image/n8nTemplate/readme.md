# n8n Workflow Setup Guide

This guide will help you quickly set up and run the n8n workflow for data transformation tasks in your internal project.

---

## 1. Create and Import the Workflow

1. **Create a new workflow** in your n8n instance.
2. **Import the provided `transformation.json`** file to load the pre-built workflow steps.

---

## 2. Configure the PostgresDB Connection

When configuring the PostgresDB node in your workflow, use the following dynamic expressions to automatically pull connection details from the initial input step (`Step 1: Capture Input`):

- **Host:**
  ```
  {{ $("Step 1: Capture Input").first().json.db_host }}
  ```
- **Database:**
  ```
  {{ $("Step 1: Capture Input").first().json.db_name }}
  ```
- **User:**
  ```
  {{ $("Step 1: Capture Input").first().json.db_user }}
  ```
- **Password:**
  ```
  {{ $("Step 1: Capture Input").first().json.db_password }}
  ```
- **Port:**
  ```
  {{ $("Step 1: Capture Input").first().json.db_port }}
  ```

---

## 3. Set Up the OpenRouter API Key

Some steps in the workflow interact with GROQ services via OpenRouter. For this, you need to set your API key in n8n.

- **API Key (example, safe for internal use):**
  ```
  ```
- In n8n, go to **Credentials** and add a new credential for OpenRouter or set it as an environment variable if required by your node.

> **Note:** Since this is an internal project, it's fine to use the above API key directly in your configuration.

---

## 4. Execute the Workflow

After importing the workflow and configuring the PostgresDB connection and API key, you can execute the workflow to perform your data transformation tasks.

---

**Tips for Smooth Execution:**
- Double-check that all required environment variables and credentials are set in your n8n instance.
- Make sure your database containers are running and accessible from n8n.

---

## Example: Triggering the Transformation via API
  ```
 curl -X GET \
  http://localhost:5678/webhook-test/sql-transformation \
  -H 'Content-Type: application/json' \
  -d '{
  "transformation": "Create a summary table with customer orders",
  "tool": "dbt",
  "schema_name": "public",
  "db_host": "postgres_destination",
  "db_port": 5432,
  "db_name": "mydatabase",
  "db_user": "user",
  "db_password": "password",
  "db_ssl": false
  }'
    ```
