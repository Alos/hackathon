
import argparse
from github import search_github, create_pr
from google.cloud import secretmanager

# TODO: Replace with your Google Cloud project ID and Secret ID
PROJECT_ID = "your-gcp-project-id"
SECRET_ID = "github_token"

def get_github_token():
    """Gets the GitHub token from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def main():
    parser = argparse.ArgumentParser(description="Find and update API calls on GitHub.")
    parser.add_argument("api_call", help="The API call to search for.")
    parser.add_argument("changes", help="The changes to apply.")
    parser.add_argument("--base-branch", default="main", help="The base branch for the pull request.")
    parser.add_argument("--commit-message", help="The commit message for the pull request.")
    args = parser.parse_args()

    github_token = get_github_token()

    commit_message = args.commit_message
    if not commit_message:
        commit_message = f"Update {args.api_call} to {args.changes}"

    search_results = search_github(args.api_call, github_token)

    for repo_url in search_results:
        create_pr(repo_url, args.api_call, args.changes, args.base_branch, commit_message, github_token)

if __name__ == "__main__":
    main()
