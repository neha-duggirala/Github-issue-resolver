import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_commit_by_sha(owner: str, repo: str, commit_sha: str, github_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves detailed information for a single commit using its SHA.
    This includes metadata, total additions (++), total deletions (--), 
    and detailed file differences.

    Args:
        owner (str): The account owner of the repository (e.g., 'octocat').
        repo (str): The name of the repository (e.g., 'Spoon-Knife').
        commit_sha (str): The full 40-character SHA hash of the commit.
        github_token (Optional[str]): GitHub Personal Access Token for authentication.
    
    Returns:
        Optional[Dict[str, Any]]: The detailed commit object, or None on error.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        print("Using GitHub Token for authentication.")
    else:
        print("No GitHub Token provided. Using lower rate limit for public access.")

    try:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            # Report detailed error if the request failed
            error_message = response.json().get('message', 'No error message provided.')
            print(f"Error fetching commit details (SHA: {commit_sha}):")
            print(f"  Status Code: {response.status_code}")
            print(f"  GitHub Message: {error_message}")
            print("Please ensure the SHA is correct and your GITHUB_TOKEN has 'read' access to contents.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network error occurred during API request: {e}")
        return None


OWNER = "neha-duggirala"
REPO = "Github-issue-resolver"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
COMMIT_SHA = "dd46be1685b38f9ffc9411d8158d416a883b39e0" 


if __name__ == "__main__":
    print(f"Attempting to fetch commit details for SHA: {COMMIT_SHA}...")
    
    commit_details = get_commit_by_sha(OWNER, REPO, COMMIT_SHA, GITHUB_TOKEN)

    if commit_details:
        print("\n--- Commit Details Found ---")
        
        # 3. Print key metadata
        commit_data = commit_details['commit']
        stats_data = commit_details['stats']
        
        print(f"  Commit Message: {commit_data['message'].splitlines()[0]}")
        print(f"  Author: {commit_data['author']['name']}")
        print(f"  Date: {commit_data['author']['date'][:10]}")
        
        # 4. Print Additions (++) and Deletions (--)
        print("\n--- Difference Statistics (Diff Stats) ---")
        print(f"  Total Changes: {stats_data.get('total', 0)}")
        print(f"  Additions (++): {stats_data.get('additions', 0)}")
        print(f"  Deletions (--): {stats_data.get('deletions', 0)}")
        
        # 5. Print Files Changed
        print("\n--- Files Modified ---")
        for file in commit_details['files']:
            print(f"  - File: {file['filename']}")
            print(f"    Lines Added: +{file['additions']}, Lines Deleted: -{file['deletions']}")
            # You can access the actual line-by-line diff here:
            # print(f"    Patch: \n{file.get('patch', 'No patch provided')[:200]}...")

    else:
        print("\nFailed to retrieve commit details. Check the logs above for errors.")