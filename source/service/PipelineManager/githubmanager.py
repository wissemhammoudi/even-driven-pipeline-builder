import json
from typing import Optional
import subprocess
from source.config.config import github_config

class GitManager:
    """Manages Git and GitHub operations"""
    
    def __init__(self, docker_manager):
        self.docker_manager = docker_manager
    
    def _create_github_repository(self, repo_name: str, workdir: str):
        """Create a GitHub repository"""
        body = json.dumps({
            "name": repo_name,
            "description": "Repo created from Docker container",
            "private": True
        })
        
        create_repo_result = self.docker_manager.exec_command(
            command=["curl", f"-u {github_config.github_email}:{github_config.github_token}", 
                    "https://api.github.com/user/repos", f"-d {body}"],
            workdir=workdir,
        )
        
        if not create_repo_result:
            raise RuntimeError("Failed to create GitHub repository")
        
        return create_repo_result
    
    def _initialize_and_push_git(self, repo_name: str, workdir: str):
        """Initialize git repository and push to GitHub"""
        git_commands = [
            "git init",
            f"git config --global user.name '{github_config.github_username}'",
            f"git config --global user.email '{github_config.github_email}'",
            "git add .",
            ["git", "commit", "-m", "Initial project commit"],
            "git branch -M main",
            f"git remote add origin https://{github_config.github_username}:{github_config.github_token}@github.com/{github_config.github_username}/{repo_name}.git",
            "git push -u origin main"
        ]
        
        for command in git_commands:
            self.docker_manager.exec_command(command=command, workdir=workdir)
    
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
                print(f"No content found in workdir {workdir}, skipping GitHub push")
                return
            
            print(f"Found content in {workdir}, proceeding with GitHub push...")
            
            self._create_github_repository(repo_name, workdir)
            
            self._initialize_and_push_git(repo_name, workdir)
                
        except Exception as e:
            print(f"Warning: Error pushing code to GitHub: {str(e)}")

    def pull_from_github(self, container_name: str):
        """Pull code from GitHub repository"""
        try:
            if not self.docker_manager.container:
                print("Warning: Container not initialized. Cannot pull code.")
                return
                
            repo_name = f"{container_name.split('_')[0]}_{container_name.split('_')[1]}"
            
            print(f"Attempting to pull code from GitHub repository: {repo_name}")
            
            clone_result = self.docker_manager.exec_command(
                command=f"git clone https://{github_config.github_username}:{github_config.github_token}@github.com/{github_config.github_username}/{repo_name}.git"
            )
            
            if not clone_result or "fatal:" in clone_result.lower():
                print(f"Warning: Failed to clone repository '{repo_name}'. It might not exist or there could be an authentication issue. Continuing without pulling.")
                return
            
            print(f"Successfully cloned repository '{repo_name}'.")
                
        except Exception as e:
            print(f"Warning: An unexpected error occurred during git pull: {str(e)}. Continuing without pulling.")