import time
import docker
from typing import Optional
from source.service.PipelineManager.dockermanager import DockerManager


class N8NManager:
    
    def __init__(self, container_name: str = "n8n"):
        self.container_name = container_name
        self.docker_manager = None
        self.container = None
    
    def initialize_n8n(self) -> bool:
        try:
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            self.container = client.containers.get(self.container_name)
            
            self.docker_manager = DockerManager()
            self.docker_manager.container = self.container            
            
            if not self._wait_for_n8n_ready():
                print("N8N not available, skipping workflow setup")
                return False
            
            self._import_credentials()
            

            self._import_workflow()
            
            self._update_workflows()
            
            self._restart_container()
            
            print("N8N initialization completed successfully")
            return True
            
        except docker.errors.NotFound:
            print(f"N8N container '{self.container_name}' not found, skipping workflow setup")
            return False
        except Exception as e:
            print(f"Error initializing N8N: {e}")
            return False
    
    def _wait_for_n8n_ready(self, max_retries: int = 30) -> bool:
        for i in range(max_retries):
            try:
                result = self.docker_manager.exec_command("n8n --version", workdir="/home/node")
                if result:
                    print("N8N is ready")
                    return True
            except:
                if i == max_retries - 1:
                    return False
                time.sleep(2)
        return False
    
    def _import_credentials(self) -> None:
        try:
            result = self.docker_manager.exec_command(
                "n8n import:credentials --input=credentials/credentials.json",
                workdir="/home/node"
            )
            if result:
                print("N8N credentials imported successfully")
            else:
                print("Failed to import credentials")
        except Exception as e:
            print(f"Error importing credentials: {e}")
    
    def _import_workflow(self) -> None:
        try:
            result = self.docker_manager.exec_command(
                "n8n import:workflow --input=workflows/transformationegent.json",
                workdir="/home/node"
            )
            if result:
                print("N8N workflow imported successfully")
            else:
                print("Failed to import workflow")
        except Exception as e:
            print(f"Error importing workflow: {e}")
    
    def _update_workflows(self) -> None:
        try:
            result = self.docker_manager.exec_command(
                "n8n update:workflow --all --active=true",
                workdir="/home/node"
            )
            if result:
                print("N8N workflows updated and activated successfully")
            else:
                print("Failed to update workflows")
        except Exception as e:
            print(f"Error updating workflows: {e}")
    
    def _restart_container(self) -> None:
        try:
            print("Restarting N8N container to apply changes...")
            self.container.restart()
            print("N8N container restarted successfully")
        except Exception as e:
            print(f"Error restarting N8N container: {e}")
