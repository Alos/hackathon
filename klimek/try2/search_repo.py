import argparse
import base64
import os
import sys
from github import Auth, Github, GithubException

def search_github_repository(repo_url, search_string, token=None):
    """
    Searches a public GitHub repository for a given string using the PyGithub library.

    Args:
        repo_url (str): The URL of the public GitHub repository.
        search_string (str): The string to search for.
        token (str, optional): GitHub personal access token for authentication.
    """
    try:
        owner, repo_name = repo_url.strip("/").split("/")[-2:]
    except ValueError:
        print(f"Error: Invalid GitHub repository URL: {repo_url}", file=sys.stderr)
        sys.exit(1)

    auth = Auth.Token(token) if token else None
    g = Github(auth=auth)

    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        contents = repo.get_contents("")
        _search_directory(contents, search_string, repo)
    except GithubException as e:
        print(f"Error accessing GitHub repository: {e.data.get('message', e.status)}", file=sys.stderr)
        if e.status == 404:
            print(f"Please ensure the repository exists and is public.", file=sys.stderr)
        elif e.status == 401:
            print(f"Authentication failed. Please check your token.", file=sys.stderr)
        sys.exit(1)


def _search_directory(contents, search_string, repo):
    """
    Recursively searches a directory in the repository.
    """
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            _check_file_content(file_content, search_string)


def _check_file_content(item, search_string):
    """
    Checks the content of a single file for the search string.
    """
    try:
        if item.encoding == "base64":
            decoded_content = base64.b64decode(item.content).decode("utf-8", "ignore")
            for i, line in enumerate(decoded_content.splitlines(), 1):
                if search_string in line:
                    print(f"{item.path}:{i}: {line.strip()}")
    except Exception as e:
        print(f"An error occurred processing file {item.path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search for a string in a public GitHub repository."
    )
    parser.add_argument("repo_url", help="The URL of the GitHub repository (e.g., https://github.com/user/repo).")
    parser.add_argument("search_string", help="The string to search for.")
    parser.add_argument(
        "--token",
        help="GitHub personal access token (or set GITHUB_TOKEN environment variable).",
        default=os.environ.get("GITHUB_TOKEN"),
    )

    args = parser.parse_args()
    search_github_repository(args.repo_url, args.search_string, args.token)
