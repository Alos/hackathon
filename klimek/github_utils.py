
from github import Github
from utils import apply_changes
import os

def search_github(api_call, github_token):
    """
    Searches for a given API call on GitHub.

    Args:
        api_call: The API call to search for.
        github_token: The GitHub personal access token.

    Returns:
        A list of repository URLs that contain the API call.
    """
    g = Github(github_token)
    results = g.search_code(query=api_call)
    repo_urls = []
    for result in results:
        repo_urls.append(result.repository.html_url)
    return repo_urls

def create_pr(repo_url, old_api_call, new_api_call, base_branch, commit_message, github_token):
    """
    Creates a pull request on GitHub.

    Args:
        repo_url: The URL of the repository to create the PR for.
        old_api_call: The old API call to replace.
        new_api_call: The new API call to replace it with.
        base_branch: The base branch for the pull request.
        commit_message: The commit message for the pull request.
        github_token: The GitHub personal access token.
    """
    g = Github(github_token)
    repo_name = repo_url.replace("https://github.com/", "")
    repo = g.get_repo(repo_name)
    
    # Create a fork
    fork = g.get_user().create_fork(repo)
    
    # Create a new branch
    branch_name = f"update-api-call-{old_api_call}"
    base = fork.get_branch(base_branch)
    try:
        fork.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
    except Exception as e:
        print(f"Branch {branch_name} may already exist: {e}")


    # Apply the changes
    contents = fork.get_contents("", ref=branch_name)
    for content_file in contents:
        if content_file.type == "file":
            try:
                file_content = content_file.decoded_content.decode()
                if old_api_call in file_content:
                    new_content = file_content.replace(old_api_call, new_api_call)
                    fork.update_file(content_file.path, commit_message, new_content, content_file.sha, branch=branch_name)
            except Exception as e:
                print(f"Could not process file {content_file.path}: {e}")


    # Create the PR
    try:
        repo.create_pull(title=commit_message, body="", head=f"{g.get_user().login}:{branch_name}", base=base_branch)
    except Exception as e:
        print(f"Could not create pull request: {e}")
