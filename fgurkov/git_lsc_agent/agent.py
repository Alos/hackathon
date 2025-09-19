from google.adk.agents import Agent
import os
import base64
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


def checkout_repository(repo_url: str) -> dict:
    """
    Clones a GitHub repository to a temporary directory and returns the path.
    Args:
        repo_url: The url of the repository (e.g., 'user/repo-url').
    Returns:
        dict: A dictionary containing the local file system location of the repo with a 'status' key ('success' or 'error') and a 'local_path' key with the directory if successful, or an 'error_message' if an error occurred.
    """
    try:
        owner, repo_name = repo_url.strip("/").split("/")[-2:]
    except ValueError:
        print(f"Error: Invalid GitHub repository URL: {repo_url}", file=sys.stderr)
        sys.exit(1)

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{owner}/{repo_name}")
        contents = repo.get_contents("")
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        _checkout_directory(contents, repo, temp_dir)        
        
        return {"status": "success", "local_path": temp_dir}
    except Exception as e:
        # Clean up the temp directory on error
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return {"status": "error", "message": str(e)}

def _checkout_directory(contents, repo, temp_dir):
    """
    Recursively searches a directory in the repository.
    """
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            _check_file_content(file_content, temp_dir)


def _check_file_content(item, temp_dir):
    """
    Writes the content of a single file to a temporary directory.
    """
    try:
        # Construct the full path for the new file in the temp directory
        file_path = os.path.join(temp_dir, item.path)
        
        # Ensure the directory structure exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Decode the file content and write it to the new file
        if item.encoding == "base64":
            decoded_content = base64.b64decode(item.content)
            with open(file_path, "wb") as f:
                f.write(decoded_content)
            
            print(f"Successfully wrote file to {file_path}")
            return {"status": "success", "file_path": file_path}
            
    except Exception as e:
        print(f"An error occurred writing file {item.path}: {e}", file=sys.stderr)
        return {"status": "error", "error_message": str(e)}


root_agent = Agent(
    name="git_lsc_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="I can answer your questions about the time and weather in a city.",
    tools=[list_repositories, checkout_repository]
)