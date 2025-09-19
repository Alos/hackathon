from google.adk.agents import Agent
import os
import shutil
import tempfile
from github import Github
from git import Repo

# Get your GitHub Personal Access Token from an environment variable
GITHUB_TOKEN = os.getenv("HACKATHON_GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

def list_repositories()->dict:
    """
    Retrieves the list of GitHub repositories accessible to the authenticated user.

    Returns:
        dict: A dictionary containing the list of repositories with a 'status' key ('success' or 'error') and a 'repositories' key with the list of repositories as a name and url pairs if successful, or an 'error_message' if an error occurred.
    """
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        repos = user.get_repos()
        
        # Create a list of dictionaries, where each dictionary contains the repo name and URL
        repo_data = [{"name": repo.name, "url": repo.html_url} for repo in repos]
        
        return {
            "status": "success",
            "repositories": repo_data
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


def checkout_repository(repo_name: str) -> dict:
    """
    Clones a GitHub repository to a temporary directory and returns the path.
    Args:
        repo_name: The name of the repository (e.g., 'user/repo-name').
    Returns:
        dict: A dictionary containing the local file system location of the repo with a 'status' key ('success' or 'error') and a 'local_path' key with the directory if successful, or an 'error_message' if an error occurred.
    """
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Construct the authenticated clone URL
        clone_url = f"https://oauth2:{GITHUB_TOKEN}@github.com/{repo_name}.git"
        
        # Clone the repository
        Repo.clone_from(clone_url, temp_dir)
        
        return {"status": "success", "local_path": temp_dir}
    except Exception as e:
        # Clean up the temp directory on error
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return {"status": "error", "message": str(e)}

root_agent = Agent(
    name="git_lsc_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="I can answer your questions about the time and weather in a city.",
    tools=[list_repositories, checkout_repository]
)