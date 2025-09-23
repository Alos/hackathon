from google.adk.agents import Agent
import os
import base64
import re
import glob
import uuid
import shutil
import sys
import tempfile
from github import Github
from git import Repo

# Get your GitHub Personal Access Token from an environment variable
GITHUB_TOKEN = os.getenv("HACKATHON_GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

checked_out_repos = {}

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
        repo_data = [{"name": repo.name, "repo_url": repo.html_url} for repo in repos]
        
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
        repo_url: The url of the repository (e.g., 'https://github.com/user/repo-url').
    Returns:
        dict: A dictionary containing the local file system location of the repo with a 'status' key ('success' or 'error') and a 'local_path' key with the directory if successful, or an 'error_message' if an error occurred.
    """
    global checked_out_repos
    try:
        repo_name = repo_url.split('/')[-1]
        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(repo_url + ".git", temp_dir, env={"GIT_USERNAME": "x-access-token", "GIT_PASSWORD": GITHUB_TOKEN})
        checked_out_repos[repo_name] = temp_dir
        return {"status": "success", "local_path": temp_dir, "repo_name": repo_name}
    except Exception as e:
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


def refactor_files_by_pattern(repo_name: str, file_pattern: str, regex_pattern: str, replacement_string: str) -> dict:
    """
    Applies a regex-based refactoring to all files matching a pattern in a checked-out repository.

    Args:
        repo_name: The name of the repository to refactor.
        file_pattern: The glob pattern to find files to refactor (e.g., '*.py', 'src/**/*.js').
        regex_pattern: The regex pattern to search for.
        replacement_string: The string to replace the matched pattern with.

    Returns:
        A dictionary with a 'status' key ('success' or 'error') and a 'message' key.
    """
    local_path = checked_out_repos.get(repo_name)
    if not local_path:
        return {"status": "error", "message": f"Repository '{repo_name}' not found. Please check it out first."}

    try:
        # Create the full search path by joining local_path and file_pattern
        search_path = os.path.join(local_path, file_pattern)
        
        # Find all files matching the pattern
        files_to_refactor = glob.glob(search_path, recursive=True)
        
        if not files_to_refactor:
            return {"status": "success", "message": f"No files found matching pattern: {file_pattern}"}

        refactored_files = []
        for file_path in files_to_refactor:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()

                new_content = re.sub(regex_pattern, replacement_string, content)

                if content != new_content:
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    refactored_files.append(file_path)

        return {"status": "success", "message": f"Refactored {len(refactored_files)} files.", "refactored_files": refactored_files}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def show_diff(repo_name: str) -> dict:
    """
    Shows the diff of a checked-out local repository.

    Args:
        repo_name: The name of the repository to show the diff for.

    Returns:
        A dictionary with a 'status' key ('success' or 'error'), a 'diff' key with the diff content, and a 'message' key.
    """
    local_path = checked_out_repos.get(repo_name)
    if not local_path:
        return {"status": "error", "message": f"Repository '{repo_name}' not found. Please check it out first."}

    try:
        repo = Repo(local_path)
        diff = repo.git.diff()
        return {"status": "success", "diff": diff}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def commit_and_create_pr(repo_name: str, commit_message: str, pr_title: str, pr_body: str) -> dict:
    """
    Commits changes to the local repository and creates a pull request.

    Args:
        repo_name: The name of the repository.
        commit_message: The commit message.
        pr_title: The title of the pull request.
        pr_body: The body of the pull request.

    Returns:
        A dictionary with a 'status' key ('success' or 'error') and a 'message' or 'pr_url' key.
    """
    local_path = checked_out_repos.get(repo_name)
    if not local_path:
        return {"status": "error", "message": f"Repository '{repo_name}' not found. Please check it out first."}

    try:
        repo = Repo(local_path)
        
        # Create a new branch
        branch_name = f"refactor-{uuid.uuid4().hex[:8]}"
        repo.create_head(branch_name)
        repo.heads[branch_name].checkout()

        # Add and commit changes
        repo.git.add(A=True)
        repo.index.commit(commit_message)

        # Push changes with authentication
        origin = repo.remote(name='origin')
        with repo.git.custom_environment(GIT_USERNAME='x-access-token', GIT_PASSWORD=GITHUB_TOKEN):
            origin.push(refspec=f'{branch_name}:{branch_name}')

        # Create a pull request
        g = Github(GITHUB_TOKEN)
        remote_url = origin.url
        owner_repo = remote_url.split('/')[-2:]
        owner, repo_name_from_url = owner_repo[0], owner_repo[1].replace('.git', '')
        
        gh_repo = g.get_repo(f"{owner}/{repo_name_from_url}")
        pr = gh_repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base=gh_repo.default_branch)

        return {"status": "success", "pr_url": pr.html_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def remove_local_repo(repo_name: str) -> dict:
    """
    Removes a local copy of a repository.

    Args:
        repo_name: The name of the repository to remove.

    Returns:
        A dictionary with a 'status' key ('success' or 'error') and a 'message' key.
    """
    local_path = checked_out_repos.pop(repo_name, None)
    if not local_path:
        return {"status": "error", "message": f"Repository '{repo_name}' not found."}

    try:
        shutil.rmtree(local_path)
        return {"status": "success", "message": f"Repository '{repo_name}' removed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


root_agent = Agent(
    name="git_lsc_agent",
    model="gemini-2.0-flash",
    description="An agent that can list a user's GitHub repositories and check them out to a local directory.",
    instruction="I can help you list your GitHub repositories and check them out. Please provide the repository URL when you want to check out a repository. You can get the URL by listing the repositories first.",
    tools=[list_repositories, checkout_repository, refactor_files_by_pattern, show_diff, commit_and_create_pr, remove_local_repo]
)