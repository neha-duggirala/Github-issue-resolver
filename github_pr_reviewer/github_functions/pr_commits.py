import os
import requests
from dotenv import load_dotenv
from google.genai import types
load_dotenv()
from typing import List, Dict, Any, Optional

github_token = os.environ["GITHUB_TOKEN"]

def _github_api_request(
    url: str, params: Optional[Dict[str, Any]] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Helper function to make a GET request to the GitHub API, handling headers and pagination.
    """

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Add Authorization header if a token is provided
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    all_results = []
    current_page_url = url
    current_params = params

    while current_page_url:
        try:
            # Determine if we need to use parameters (only on the first request)
            if current_page_url == url and current_params:
                response = requests.get(
                    current_page_url, headers=headers, params=current_params
                )
            else:
                response = requests.get(current_page_url, headers=headers)

            if response.status_code == 200:
                page_results = response.json()
                all_results.extend(page_results)

                # Check for the 'next' link in the Link header for pagination
                if "next" in response.links:
                    current_page_url = response.links["next"]["url"]
                    current_params = (
                        None  # Do not use original params on subsequent pages
                    )
                else:
                    current_page_url = None  # End pagination

            else:
                error_message = response.json().get(
                    "message", "No error message provided."
                )
                print(
                    f"Error fetching data from {url}. Status Code: {response.status_code}"
                )
                print(f"GitHub Message: {error_message}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request to {url}: {e}")
            return None

    return all_results


# --------------------------------------------------------------------------------


def list_pr_commits(
    owner: str, repo: str, pull_number: int
) -> Optional[List[Dict[str, Any]]]:
    """
    Lists all commit objects (summary info) for a specific Pull Request, handling pagination.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        pull_number (int): The number that identifies the pull request.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of commit objects (dictionaries),
                                        or None on error.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/commits"

    # Max results per page for this endpoint is 100
    params = {"per_page": 100}

    print(f"Fetching commits for PR #{pull_number} in {owner}/{repo}...")

    # Call the helper function to fetch all pages of commits
    commits = _github_api_request(api_url, params=params)

    return commits


# --------------------------------------------------------------------------------


def get_commit_by_sha(owner: str, repo: str, sha: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the detailed commit object for a given SHA, including stats and file changes.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error fetching commit details for {sha}. Status Code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request for commit {sha}: {e}")
        return None


# --------------------------------------------------------------------------------


def get_pr_commit_details(owner: str, repo: str, pull_number: int) -> str:
    """
    Fetches and formats detailed information (summary + diff stats) for all commits in a PR
    into a single, readable string.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        pull_number (int): The number that identifies the pull request.

    Returns:
        str: A multi-line string containing the formatted commit details.
    """
    output = []

    # 1. Get the list of commits (summary info)
    pr_commits = list_pr_commits(owner, repo, pull_number)

    if pr_commits:
        output.append(f"\n--- Found {len(pr_commits)} Commits in PR #{pull_number} ---")

        # 2. Iterate through each commit to get details
        for i, commit in enumerate(pr_commits):
            sha = commit.get("sha", "N/A")
            short_sha = sha[:7]
            message_summary = (
                commit.get("commit", {}).get("message", "No message").splitlines()[0]
            )
            author_name = (
                commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            )

            output.append(
                f'\n{i+1}. SHA: {short_sha} | Author: {author_name} | Message: "{message_summary}"'
            )

            # Fetch full commit details for diff stats
            commit_details = get_commit_by_sha(owner, repo, sha)

            if commit_details:
                output.append(f"  --- Detailed Stats for Commit ({short_sha}) ---")

                commit_data = commit_details.get("commit", {})
                stats_data = commit_details.get("stats", {})
                files_data = commit_details.get("files", [])

                # 3. Print key metadata
                output.append(
                    f"  Commit Message: {commit_data.get('message', 'N/A').splitlines()[0]}"
                )
                output.append(
                    f"  Author: {commit_data.get('author', {}).get('name', 'N/A')}"
                )
                output.append(
                    f"  Date: {commit_data.get('author', {}).get('date', 'N/A')[:10]}"
                )

                # 4. Print Additions (++) and Deletions (--)
                # output.append("\n  --- Difference Statistics (Diff Stats) ---")
                # output.append(f"  Total Changes: {stats_data.get('total', 0)}")
                # output.append(f"  Additions (++): {stats_data.get('additions', 0)}")
                # output.append(f"  Deletions (--): {stats_data.get('deletions', 0)}")

                # 5. Print Files Changed
                output.append("\n  --- Files Modified ---")
                for file in files_data:
                    output.append(f"  - File: {file.get('filename', 'N/A')}")
                    output.append(
                        f"    Lines Added: +{file.get('additions', 0)}, Lines Deleted: -{file.get('deletions', 0)}"
                    )
                    # Append patch content (truncated for brevity)
                    patch = file.get("patch", "No patch provided.")
                    # Truncate to a reasonable length for the output string
                    output.append(f"    Patch (snippet): \n    {patch[:200]}...")
            else:
                output.append(
                    f"  [ERROR] Could not fetch detailed stats for commit {short_sha}. Skipping details."
                )

    else:
        output.append(f"\nFailed to retrieve commits for PR #{pull_number}.")
        output.append(
            "Please check the owner/repo/PR number and ensure the GITHUB_TOKEN is valid if the repository is private."
        )

    return "\n".join(output)

schema_get_pr_commit_details = types.FunctionDeclaration(
    name="get_pr_commit_details",
    description="Fetches and formats detailed information (summary + diff stats) for all commits in a PR into a single, readable string.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "owner": types.Schema(
                type=types.Type.STRING,
                description="The repository owner.",
            ),
            "repo": types.Schema(
                type=types.Type.STRING,
                description="The repository name.",
            ),
            "pull_number": types.Schema(
                type=types.Type.INTEGER,
                description="The number that identifies the pull request.",
            ),
        },
    ),
)



if __name__ == "__main__":

    print("=" * 50)

    # Use the new function to capture the output
    detailed_commit_report = get_pr_commit_details(OWNER, REPO, PULL_NUMBER)

    # Print the resulting string only once
    print(detailed_commit_report)
    print("=" * 50)
