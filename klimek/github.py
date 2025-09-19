
import os
import requests
import subprocess
from utils import apply_changes
from constants import GITHUB_API_URL

def search_github(api_call, github_token):
    """
    Searches for a given API call on GitHub.

    Args:
        api_call: The API call to search for.
        github_token: The GitHub personal access token.

    Returns:
        A list of repository URLs that contain the API call.
    """

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"{GITHUB_API_URL}/search/code?q={api_call}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error searching GitHub: {e}")
        return []

    results = response.json()
    repo_urls = [item["repository"]["html_url"] for item in results["items"]]

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

    repo_name = repo_url.split("/")[-1]
    repo_dir = f"/tmp/{repo_name}"

    # Clone the repository
    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_url}: {e}")
        return

    # Create a new branch
    branch_name = f"update-api-call-{old_api_call}"
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_dir)

    # Apply the changes
    for root, _, files in os.walk(repo_dir):
        for file in files:
            file_path = os.path.join(root, file)
            apply_changes(file_path, old_api_call, new_api_call)

    # Commit the changes
    subprocess.run(["git", "add", "."], cwd=repo_dir)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_dir)

    # Push the changes to GitHub
    try:
        subprocess.run(["git", "push", "origin", branch_name], cwd=repo_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error pushing changes to GitHub: {e}")
        return

    # Create the PR
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"{GITHUB_API_URL}/repos/{repo_url.replace('https://github.com/', '')}/pulls"

    data = {
        "title": commit_message,
        "head": branch_name,
        "base": base_branch,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error creating PR: {e}")
