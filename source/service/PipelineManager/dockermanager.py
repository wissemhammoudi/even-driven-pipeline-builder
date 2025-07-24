import docker
import time
from typing import Dict, Any, Optional
from source.config.config import DockerConfig

class DockerManager:
    """Manages Docker container operations"""
    
    def __init__(self):
        self.client = docker.DockerClient(base_url=DockerConfig.Docker_Client_Base_Url)
        self.container = None
        
    def _create_container_config(self, name: str, image: str, port: Optional[int] = None) -> Dict[str, Any]:
        """Create container configuration"""
        install_command = "sleep infinity"
        container_config = {
            "image": image,
            "entrypoint": ["sh", "-c"],
            "command": [install_command],
            "name": name,
            "environment": {
                "MELTANO__CORE__ENABLED_PLUGINS": "singer",
                "MELTANO__CORE__ENV": "production",
            },
            "working_dir": "/project",
            "stdin_open": True,
            "tty": True,
            "detach": True,
            "mem_limit": "4g",
        }
        
        if port is not None:
            container_config["ports"] = {
                "8088/tcp": None
            }
            
        return container_config

    def create_container(self, name: str, image: str, port: Optional[int] = None):
        """Create and start a Docker container"""
        try:
            container_config = self._create_container_config(name, image, port)
            
            container_id = self.client.containers.run(**container_config)
            self.container = self.client.containers.get(container_id.id)
            
            network = self.client.networks.get("near-realtime-data-pipeline_default")
            network.connect(self.container)

            self._wait_for_container()
            print(f"Container '{name}' created successfully!")
            return self.container
            
        except Exception as e:
            print(f"Failed to create container: {e}")
            raise RuntimeError(f"Failed to create container: {str(e)}")

    def stop_container(self):
        """Stop and remove the container"""
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
                print(f"Stopped container {self.container.id[:12]}")
            except Exception as e:
                print(f"Error stopping container: {e}")
            finally:
                self.container = None

    def _wait_for_container(self, timeout: int = 10):
        """Wait for container to be ready"""
        for _ in range(timeout):
            if self.container.status in ["created", "running"]:
                break
            time.sleep(1)
            self.container.reload()

    def exec_command(self, command: str="", retries=1, workdir: str="/project", run_in_background: bool=False):
        if not self.container:
            raise RuntimeError("Container not initialized. Cannot execute command.")        
        if run_in_background:
            try:
                exec_result = self.container.exec_run(
                    cmd=(command.split() if isinstance(command, str) else command),
                    workdir=workdir,
                    detach=run_in_background  
                )
                print(f"Command started in background: {command}")
                return f"Background execution started for: {command}"
            except Exception as e:
                error_msg = f"Background execution error: {str(e)}"
                print(error_msg)
                raise RuntimeError(error_msg)
        
        for attempt in range(retries):
            try:
                exit_code, output = self.container.exec_run(
                    cmd=(command.split() if isinstance(command, str) else command),
                    workdir=workdir,
                )
                if exit_code == 0:
                    return output.decode('utf-8')
                error_msg = f"Command failed (attempt {attempt+1}/{retries}): {output.decode('utf-8')}"
                print(error_msg)
                if attempt == retries - 1:
                    raise RuntimeError(error_msg)
            except Exception as e:
                error_msg = f"Execution error: {str(e)}"
                print(error_msg)
                if attempt == retries - 1:  
                    raise RuntimeError(error_msg)
            time.sleep(2)
        return None


    def get_container_name(self) -> Optional[str]:
        """Get container name"""
        return self.container.name if self.container else None