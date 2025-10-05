import json
from typing import Optional
import subprocess
from source.config.config import github_config



class GitManager:
    """Manages Git and GitHub operations"""
    
    def __init__(self, docker_manager):
        self.docker_manager = docker_manager
        self._validate_github_credentials()
    
    def _validate_github_credentials(self):
        """Validate GitHub credentials before attempting operations"""

        if not github_config.github_token:
            raise RuntimeError("GitHub token is not configured")
        
        if not github_config.github_username:
            raise RuntimeError("GitHub username is not configured")
        
        if not github_config.github_email:
            raise RuntimeError("GitHub email is not configured")
        
        try:
            test_result = self.docker_manager.exec_command(
                command=["curl", "-s", "-H", f"Authorization: token {github_config.github_token}", 
                        "https://api.github.com/user"],
                workdir="/"
            )
            
            if not test_result:
                raise RuntimeError("Failed to test GitHub API connection")
                
        except Exception as e:
            raise RuntimeError(f"GitHub API connection test failed: {str(e)}")
    
    def _create_github_repository(self, repo_name: str, workdir: str):
        """Create a GitHub repository"""
        
        body = json.dumps({
            "name": repo_name,
            "description": "Repo created from Docker container",
            "private": True
        })
        
        try:
            create_repo_result = self.docker_manager.exec_command(
                command=["curl", "-v", f"-u {github_config.github_email}:{github_config.github_token}", 
                        "https://api.github.com/user/repos", f"-d {body}"],
                workdir=workdir,
            )
            
            if not create_repo_result:
                raise RuntimeError("Failed to create GitHub repository - No response from API")
            
            if "error" in create_repo_result.lower() or "fatal" in create_repo_result.lower():
                raise RuntimeError(f"Failed to create GitHub repository - API Error: {create_repo_result}")
            
            return create_repo_result
            
        except Exception as e:
            raise RuntimeError(f"Failed to create GitHub repository: {str(e)}")
    
    def _initialize_and_push_git(self, repo_name: str, workdir: str):
        """Initialize git repository and push to GitHub"""
        
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
            try:
                result = self.docker_manager.exec_command(command=command, workdir=workdir)
            except Exception as e:
                raise RuntimeError(f"Git command failed: {' '.join(command)} - Error: {str(e)}")
    
    def push_to_github(self, container_name: str, workdir: str):
        """Push code to GitHub repository"""    
        
        if not self.docker_manager.container:
            raise RuntimeError("Container not initialized. Cannot push code.")

        repo_name = f"{container_name.split('_')[0]}_{container_name.split('_')[1]}"
        
        try:
            check_dir_result = self.docker_manager.exec_command(
                command=["sh", "-c", f"if [ -d '{workdir}' ] && [ \"$(ls -A {workdir})\" ]; then echo 'exists_with_content'; else echo 'empty_or_not_exists'; fi"],
                workdir="/"
            )
            
            if not check_dir_result or 'empty_or_not_exists' in check_dir_result:
                return
            
            self._create_github_repository(repo_name, workdir)
            
            self._initialize_and_push_git(repo_name, workdir)
                
        except Exception as e:
            raise RuntimeError(f"Failed to push code to GitHub: {str(e)}")

    def pull_from_github(self, container_name: str):
        """Pull code from GitHub repository"""
        
        try:
            if not self.docker_manager.container:
                return
                
            repo_name = f"{container_name.split('_')[0]}_{container_name.split('_')[1]}"
            
            clone_result = self.docker_manager.exec_command(
                command=["git", "clone", f"https://{github_config.github_username}:{github_config.github_token}@github.com/{github_config.github_username}/{repo_name}.git"]
            )
            
            if not clone_result or "fatal:" in clone_result.lower():
                return
                
        except Exception as e:
            pass