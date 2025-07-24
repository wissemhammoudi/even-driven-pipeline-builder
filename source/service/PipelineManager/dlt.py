from typing import Dict, Any
import json
from source.service.PipelineManager.interface import BaseStepRunner

class DltRunner(BaseStepRunner):
    def __init__(self):
        self.container = None  
        self.docker_manager = None  

    def config(self, step: Dict[str, Any], name: str) -> None:
        """Configure DLT pipeline step"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot configure.")
            
        try:
            container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
            step_config = step["config"].step_config
            workdir = f"/project/{container_name}"
            
            self.docker_manager.exec_command(
                command=["mkdir", "-p", workdir],
                workdir="/project"
            )
            
            self.docker_manager.exec_command(
                command=[
                    "uv", "run", "dlt", "--non-interactive", "init",
                    step_config["source"], step_config["destination"]
                ],
                workdir=workdir
            )
            
            secrets_content = []
            secrets_content.append(f'[sources.{step_config["source"]}.credentials]')
            for key, value in step_config["connection_config"]["source"].items():
                escaped_value = str(value).replace('"', '\\"')
                secrets_content.append(f'{key} = "{escaped_value}"')

            secrets_content.append(f'\n[destination.{step_config["destination"]}.credentials]')
            for key, value in step_config["connection_config"]["destination"].items():
                escaped_value = str(value).replace('"', '\\"')
                secrets_content.append(f'{key} = "{escaped_value}"')

            secrets_str = "\n".join(secrets_content)
            
            self.docker_manager.exec_command(
                command=["mkdir", "-p", f"{workdir}/.dlt"],
                workdir=workdir
            )
            
            self.docker_manager.exec_command(
                command=[
                    "sh", "-c",
                    f"cat << 'EOF' > {workdir}/.dlt/secrets.toml\n{secrets_str}\nEOF"
                ],
                workdir=workdir
            )

            config_data = {
                "pipeline_name": f'{step_config["source"]}_{step_config["destination"]}',
                "target_schema": step_config["target_schema"],
                "tables": step_config["table_sync_config"]
            }

            json_str = json.dumps(config_data, indent=2)
            escaped_json = json_str.replace("'", "'\"'\"'").replace("$", "\\$")
            
            self.docker_manager.exec_command(
                command=["mkdir", "-p", f"{workdir}/config"],
                workdir=workdir
            )
            
            self.docker_manager.exec_command(
                command=[
                    "sh", "-c",
                    f"cat << 'EOF' > {workdir}/config/config.json\n{escaped_json}\nEOF"
                ],
                workdir=workdir
            )

            self.docker_manager.exec_command(
                command=[
                    "sh", "-c",
                    f"rm -f {workdir}/*.py {workdir}/.gitignore"
                ],
                workdir=workdir
            )
            
            source_script = f"/project/{step_config['source']}_{step_config['destination']}/{step_config['source']}_{step_config['destination']}.py"
            target_script = f"{workdir}/{step_config['source']}_{step_config['destination']}.py"
            
            self.docker_manager.exec_command(
                command=[
                    "sh", "-c",
                    f"mv {source_script} {target_script} 2>/dev/null || true"
                ],
                workdir=workdir
            )

        except Exception as e:
            raise RuntimeError(f"Error configuring DLT: {str(e)}")

    def start(self, step: Dict[str, Any], name: str) -> None:
        """Start the DLT pipeline execution"""
        if not self.docker_manager or not self.docker_manager.container:
            raise RuntimeError("Docker manager not initialized. Cannot start.")
            
        try:
            step_config = step["config"].step_config
            container_name = f"{name.split('_')[0]}_{name.split('_')[1]}"
            workdir = f"/project/{container_name}"

            self.docker_manager.exec_command(
                command=["uv", "venv"],
                workdir=workdir
            )
            
            self.docker_manager.exec_command(
                command=["uv", "pip", "install", "-r", "requirements.txt"],
                workdir=workdir
            )

            python_script_name = f"{step_config['source']}_{step_config['destination']}.py"
            self.docker_manager.exec_command(
                command=["uv", "run", "python", python_script_name],
                workdir=workdir
            )

        except Exception as e:
            raise RuntimeError(f"Error starting DLT pipeline: {str(e)}")