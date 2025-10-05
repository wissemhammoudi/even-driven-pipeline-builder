import docker
import time
import logging
from typing import Dict, Any, Optional
from source.config.config import docker_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker container operations"""
    
    def __init__(self):
        self.client = docker.DockerClient(base_url=docker_config.Docker_Client_Base_Url)
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
        logger.info(f"🐳 Creating Docker container: {name}")
        logger.info(f"📦 Image: {image}")
        logger.info(f"🔌 Port: {port}")
        
        try:
            container_config = self._create_container_config(name, image, port)
            logger.info(f"⚙️ Container config: {container_config}")
            
            logger.info("🚀 Starting container...")
            container_id = self.client.containers.run(**container_config)
            self.container = self.client.containers.get(container_id.id)
            logger.info(f"✅ Container started with ID: {container_id.id[:12]}")
            
<<<<<<< Updated upstream
            network = self.client.networks.get("near-realtime-data-pipeline_default")
=======
            logger.info(f"🌐 Connecting to network: {docker_config.docker_network_name}")
            network = self.client.networks.get(docker_config.docker_network_name)
>>>>>>> Stashed changes
            network.connect(self.container)
            logger.info("✅ Network connection established")

            logger.info("⏳ Waiting for container to be ready...")
            self._wait_for_container()
            logger.info(f"🎉 Container '{name}' created successfully!")
            return self.container
            
        except Exception as e:
            logger.error(f"❌ Failed to create container: {str(e)}")
            logger.error(f"📊 Name: {name}, Image: {image}, Port: {port}")
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
        logger.info(f"🔧 Executing command: {' '.join(command) if isinstance(command, list) else command}")
        logger.info(f"📁 Working directory: {workdir}")
        logger.info(f"🔄 Retries: {retries}")
        logger.info(f"🔄 Background: {run_in_background}")
        
        if not self.container:
            logger.error("❌ Container not initialized. Cannot execute command.")
            raise RuntimeError("Container not initialized. Cannot execute command.")        
        
        if run_in_background:
            try:
                logger.info("🚀 Starting command in background...")
                exec_result = self.container.exec_run(
                    cmd=(command.split() if isinstance(command, str) else command),
                    workdir=workdir,
                    detach=run_in_background  
                )
                logger.info(f"✅ Command started in background: {command}")
                return f"Background execution started for: {command}"
            except Exception as e:
                error_msg = f"Background execution error: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        
        for attempt in range(retries):
            try:
                logger.info(f"🔄 Attempt {attempt+1}/{retries}...")
                exit_code, output = self.container.exec_run(
                    cmd=(command.split() if isinstance(command, str) else command),
                    workdir=workdir,
                )
                
                logger.info(f"📊 Exit code: {exit_code}")
                output_str = output.decode('utf-8')
                logger.info(f"📝 Output: {output_str}")
                
                if exit_code == 0:
                    logger.info("✅ Command executed successfully")
                    return output_str
                
                error_msg = f"Command failed (attempt {attempt+1}/{retries}): {output_str}"
                logger.warning(error_msg)
                if attempt == retries - 1:
                    logger.error(f"❌ Command failed after {retries} attempts")
                    raise RuntimeError(error_msg)
            except Exception as e:
                error_msg = f"Execution error: {str(e)}"
                logger.error(error_msg)
                if attempt == retries - 1:  
                    raise RuntimeError(error_msg)
            time.sleep(2)
        return None


    def get_container_name(self) -> Optional[str]:
        """Get container name"""
        return self.container.name if self.container else None