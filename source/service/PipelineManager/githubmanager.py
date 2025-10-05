import json
import logging
from typing import Optional
import subprocess
from source.config.config import github_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitManager:
    """Manages Git and GitHub operations"""
    
    def __init__(self, docker_manager):
        self.docker_manager = docker_manager
        self._validate_github_credentials()
    
    def _validate_github_credentials(self):
        """Validate GitHub credentials before attempting operations"""
        logger.info("🔍 Validating GitHub credentials...")
        
        if not github_config.github_token:
            logger.error("❌ GitHub token is not configured")
            raise RuntimeError("GitHub token is not configured")
        
        if not github_config.github_username:
            logger.error("❌ GitHub username is not configured")
            raise RuntimeError("GitHub username is not configured")
        
        if not github_config.github_email:
            logger.error("❌ GitHub email is not configured")
            raise RuntimeError("GitHub email is not configured")
        
        logger.info(f"✅ GitHub credentials validated:")
        logger.info(f"   👤 Username: {github_config.github_username}")
        logger.info(f"   📧 Email: {github_config.github_email}")
        logger.info(f"   🔑 Token: {'Configured' if github_config.github_token else 'Not configured'}")
        
        # Test GitHub API connection
        try:
            logger.info("🌐 Testing GitHub API connection...")
            test_result = self.docker_manager.exec_command(
                command=["curl", "-s", "-H", f"Authorization: token {github_config.github_token}", 
                        "https://api.github.com/user"],
                workdir="/"
            )
            
            if test_result and "login" in test_result:
                logger.info("✅ GitHub API connection successful")
                logger.info(f"📊 API Response: {test_result}")
            else:
                logger.warning(f"⚠️ GitHub API connection test returned unexpected result: {test_result}")
                
        except Exception as e:
            logger.warning(f"⚠️ GitHub API connection test failed: {str(e)}")
            logger.warning("⚠️ Continuing with pipeline creation, but GitHub operations may fail")
    
    def _create_github_repository(self, repo_name: str, workdir: str):
        """Create a GitHub repository"""
        logger.info(f"🔧 Creating GitHub repository: {repo_name}")
        logger.info(f"📧 Using GitHub email: {github_config.github_email}")
        logger.info(f"👤 Using GitHub username: {github_config.github_username}")
        logger.info(f"🔑 GitHub token configured: {'Yes' if github_config.github_token else 'No'}")
        
        body = json.dumps({
            "name": repo_name,
            "description": "Repo created from Docker container",
            "private": True
        })
        
        logger.info(f"📝 Repository creation payload: {body}")
        
        try:
            create_repo_result = self.docker_manager.exec_command(
                command=["curl", "-v", f"-u {github_config.github_email}:{github_config.github_token}", 
                        "https://api.github.com/user/repos", f"-d {body}"],
                workdir=workdir,
            )
            
            logger.info(f"📡 GitHub API response: {create_repo_result}")
            
            if not create_repo_result:
                logger.error("❌ No response from GitHub API")
                raise RuntimeError("Failed to create GitHub repository - No response from API")
            
            if "error" in create_repo_result.lower() or "fatal" in create_repo_result.lower():
                logger.error(f"❌ GitHub API returned error: {create_repo_result}")
                raise RuntimeError(f"Failed to create GitHub repository - API Error: {create_repo_result}")
            
            logger.info(f"✅ GitHub repository '{repo_name}' created successfully")
            return create_repo_result
            
        except Exception as e:
            logger.error(f"❌ Exception during GitHub repository creation: {str(e)}")
            raise RuntimeError(f"Failed to create GitHub repository: {str(e)}")
    
    def _initialize_and_push_git(self, repo_name: str, workdir: str):
        """Initialize git repository and push to GitHub"""
        logger.info(f"🔧 Initializing git repository in: {workdir}")
        
        git_commands = [
            ["git", "init"],
            ["git", "config", "--global", "user.name", github_config.github_username],
            ["git", "config", "--global", "user.email", github_config.github_email],
            ["git", "add", "."],
            ["git", "commit", "-m", "Initial project commit"],
            ["git", "branch", "-M", "main"],
            ["git", "remote", "add", "origin", f"https://{github_config.github_username}:{github_config.github_token}@github.com/{github_config.github_username}/{repo_name}.git"],
            ["git", "push", "-u", "origin", "main"]
        ]
        
        for i, command in enumerate(git_commands, 1):
            logger.info(f"🔄 Executing git command {i}/{len(git_commands)}: {' '.join(command)}")
            try:
                result = self.docker_manager.exec_command(command=command, workdir=workdir)
                logger.info(f"✅ Git command {i} completed successfully")
                if result:
                    logger.info(f"📝 Command output: {result}")
            except Exception as e:
                logger.error(f"❌ Git command {i} failed: {str(e)}")
                raise RuntimeError(f"Git command failed: {' '.join(command)} - Error: {str(e)}")
    
    def push_to_github(self, container_name: str, workdir: str):
        """Push code to GitHub repository"""
        logger.info(f"🚀 Starting GitHub push process for container: {container_name}")
        logger.info(f"📁 Working directory: {workdir}")
        
        if not self.docker_manager.container:
            logger.error("❌ Container not initialized. Cannot push code.")
            raise RuntimeError("Container not initialized. Cannot push code.")

        repo_name = f"{container_name.split('_')[0]}_{container_name.split('_')[1]}"
        logger.info(f"📦 Repository name: {repo_name}")
        
        try:
            logger.info(f"🔍 Checking if directory {workdir} exists and has content...")
            check_dir_result = self.docker_manager.exec_command(
                command=["sh", "-c", f"if [ -d '{workdir}' ] && [ \"$(ls -A {workdir})\" ]; then echo 'exists_with_content'; else echo 'empty_or_not_exists'; fi"],
                workdir="/"
            )
            
            logger.info(f"📋 Directory check result: {check_dir_result}")
            
            if not check_dir_result or 'empty_or_not_exists' in check_dir_result:
                logger.warning(f"⚠️ No content found in workdir {workdir}, skipping GitHub push")
                return
            
            logger.info(f"✅ Found content in {workdir}, proceeding with GitHub push...")
            
            # Create GitHub repository
            self._create_github_repository(repo_name, workdir)
            
            # Initialize and push git
            self._initialize_and_push_git(repo_name, workdir)
            
            logger.info(f"🎉 Successfully pushed code to GitHub repository: {repo_name}")
                
        except Exception as e:
            logger.error(f"❌ Error pushing code to GitHub: {str(e)}")
            logger.error(f"📊 Container: {container_name}, Workdir: {workdir}, Repo: {repo_name}")
            raise RuntimeError(f"Failed to push code to GitHub: {str(e)}")

    def pull_from_github(self, container_name: str):
        """Pull code from GitHub repository"""
        logger.info(f"📥 Starting GitHub pull process for container: {container_name}")
        
        try:
            if not self.docker_manager.container:
                logger.warning("⚠️ Container not initialized. Cannot pull code.")
                return
                
            repo_name = f"{container_name.split('_')[0]}_{container_name.split('_')[1]}"
            logger.info(f"📦 Repository name: {repo_name}")
            
            logger.info(f"🔍 Attempting to pull code from GitHub repository: {repo_name}")
            
            clone_result = self.docker_manager.exec_command(
                command=["git", "clone", f"https://{github_config.github_username}:{github_config.github_token}@github.com/{github_config.github_username}/{repo_name}.git"]
            )
            
            logger.info(f"📡 Clone result: {clone_result}")
            
            if not clone_result or "fatal:" in clone_result.lower():
                logger.warning(f"⚠️ Failed to clone repository '{repo_name}'. It might not exist or there could be an authentication issue. Continuing without pulling.")
                return
            
            logger.info(f"✅ Successfully cloned repository '{repo_name}'.")
                
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred during git pull: {str(e)}. Continuing without pulling.")