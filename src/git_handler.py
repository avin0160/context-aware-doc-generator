"""
Git repository handler for cloning and managing repositories.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import git
from git import Repo
import logging

logger = logging.getLogger(__name__)


class GitHandler:
    """Handle Git repository operations for code analysis."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize Git handler.
        
        Args:
            temp_dir: Directory for temporary clones (None for system temp)
        """
        self.temp_dir = temp_dir
        self.cloned_repos: Dict[str, str] = {}
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """
        Clone a GitHub repository to a temporary directory.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch to clone (default: main)
            
        Returns:
            Path to cloned repository
        """
        try:
            # Create temporary directory
            if self.temp_dir:
                os.makedirs(self.temp_dir, exist_ok=True)
                temp_dir = tempfile.mkdtemp(dir=self.temp_dir)
            else:
                temp_dir = tempfile.mkdtemp()
            
            logger.info(f"Cloning {repo_url} to {temp_dir}")
            
            # Clone repository
            repo = Repo.clone_from(
                repo_url, 
                temp_dir,
                branch=branch,
                depth=1  # Shallow clone for efficiency
            )
            
            # Store reference
            self.cloned_repos[repo_url] = temp_dir
            
            logger.info(f"Successfully cloned {repo_url}")
            return temp_dir
            
        except git.exc.GitCommandError as e:
            logger.error(f"Git error cloning {repo_url}: {e}")
            # Try with default branch if main doesn't exist
            if branch == "main":
                logger.info("Trying with 'master' branch")
                return self.clone_repository(repo_url, branch="master")
            raise
        except Exception as e:
            logger.error(f"Error cloning repository {repo_url}: {e}")
            raise
    
    def extract_zip_archive(self, zip_path: str) -> str:
        """
        Extract ZIP archive to temporary directory.
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            Path to extracted directory
        """
        try:
            import zipfile
            
            # Create temporary directory
            if self.temp_dir:
                os.makedirs(self.temp_dir, exist_ok=True)
                temp_dir = tempfile.mkdtemp(dir=self.temp_dir)
            else:
                temp_dir = tempfile.mkdtemp()
            
            logger.info(f"Extracting {zip_path} to {temp_dir}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the actual code directory (often nested in ZIP)
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                actual_dir = os.path.join(temp_dir, extracted_items[0])
            else:
                actual_dir = temp_dir
            
            logger.info(f"Successfully extracted to {actual_dir}")
            return actual_dir
            
        except Exception as e:
            logger.error(f"Error extracting ZIP {zip_path}: {e}")
            raise
    
    def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """
        Get information about a cloned repository.
        
        Args:
            repo_path: Path to repository directory
            
        Returns:
            Repository information
        """
        try:
            repo_info = {
                'path': repo_path,
                'name': Path(repo_path).name,
                'files_count': 0,
                'directories_count': 0,
                'total_size_mb': 0,
                'languages': set(),
                'has_git': False
            }
            
            # Check if it's a git repo
            try:
                repo = Repo(repo_path)
                repo_info['has_git'] = True
                repo_info['current_branch'] = repo.active_branch.name
                repo_info['remote_url'] = repo.remotes.origin.url if repo.remotes else None
            except:
                pass
            
            # Walk through directory
            total_size = 0
            for root, dirs, files in os.walk(repo_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.vscode', 'build', 'dist'}]
                
                repo_info['directories_count'] += len(dirs)
                repo_info['files_count'] += len(files)
                
                for file in files:
                    file_path = os.path.join(root, file) 
                    try:
                        total_size += os.path.getsize(file_path)
                        
                        # Detect language from extension
                        ext = Path(file).suffix.lower()
                        if ext in ['.py']:
                            repo_info['languages'].add('Python')
                        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                            repo_info['languages'].add('JavaScript/TypeScript')
                        elif ext in ['.java']:
                            repo_info['languages'].add('Java')
                        elif ext in ['.go']:
                            repo_info['languages'].add('Go')
                        elif ext in ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp']:
                            repo_info['languages'].add('C/C++')
                        elif ext in ['.cs']:
                            repo_info['languages'].add('C#')
                        elif ext in ['.rb']:
                            repo_info['languages'].add('Ruby')
                        elif ext in ['.php']:
                            repo_info['languages'].add('PHP')
                            
                    except OSError:
                        continue
            
            repo_info['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            repo_info['languages'] = list(repo_info['languages'])
            
            return repo_info
            
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {'path': repo_path, 'error': str(e)}
    
    def cleanup(self, repo_path: Optional[str] = None):
        """
        Clean up temporary directories.
        
        Args:
            repo_path: Specific path to clean up (None for all)
        """
        try:
            if repo_path:
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                    logger.info(f"Cleaned up {repo_path}")
                # Remove from tracking
                self.cloned_repos = {k: v for k, v in self.cloned_repos.items() if v != repo_path}
            else:
                # Clean up all tracked repositories
                for url, path in self.cloned_repos.items():
                    if os.path.exists(path):
                        shutil.rmtree(path)
                        logger.info(f"Cleaned up {path}")
                self.cloned_repos.clear()
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


# Factory function
def create_git_handler(temp_dir: Optional[str] = None) -> GitHandler:
    """Create and return a Git handler."""
    return GitHandler(temp_dir)