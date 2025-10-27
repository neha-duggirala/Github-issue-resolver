import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from config import *

load_dotenv()


def _github_api_request(url: str, params: Optional[Dict[str, Any]] = None, github_token: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Helper function to make a GET request to the GitHub API, handling headers and pagination.
    """
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
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
                response = requests.get(current_page_url, headers=headers, params=current_params)
            else:
                response = requests.get(current_page_url, headers=headers)

            if response.status_code == 200:
                page_results = response.json()
                all_results.extend(page_results)
                
                # Check for the 'next' link in the Link header for pagination
                if 'next' in response.links:
                    current_page_url = response.links['next']['url']
                    current_params = None # Do not use original params on subsequent pages
                else:
                    current_page_url = None # End pagination
            
            else:
                error_message = response.json().get('message', 'No error message provided.')
                print(f"Error fetching data from {url}. Status Code: {response.status_code}")
                print(f"GitHub Message: {error_message}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request to {url}: {e}")
            return None
            
    return all_results

# --------------------------------------------------------------------------------

def list_pr_commits(owner: str, repo: str, pull_number: int, github_token: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Lists all commit objects for a specific Pull Request, handling pagination.

    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        pull_number (int): The number that identifies the pull request.
        github_token (Optional[str]): GitHub Personal Access Token for authentication.
    
    Returns:
        Optional[List[Dict[str, Any]]]: A list of commit objects (dictionaries), 
                                        or None on error.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/commits"
    
    # Max results per page for this endpoint is 100
    params = {'per_page': 100}

    print(f"Fetching commits for PR #{pull_number} in {owner}/{repo}...")

    # Call the helper function to fetch all pages of commits
    commits = _github_api_request(api_url, params=params, github_token=github_token)

    return commits

# --------------------------------------------------------------------------------

def get_all_pr_commit_shas_from_pr_list(pr_list: List[Dict[str, Any]], github_token: Optional[str] = None) -> Dict[int, List[str]]:
    """
    Processes a list of GitHub Pull Request objects (e.g., from the Pulls API)
    to fetch and return the list of commit SHAs for each PR.

    Args:
        pr_list (List[Dict[str, Any]]): A list of dictionaries, where each 
                                        dictionary is a full PR object.
        github_token (Optional[str]): GitHub Personal Access Token for authentication.
    
    Returns:
        Dict[int, List[str]]: A dictionary mapping PR number (int) to a list of commit SHAs (str).
    """
    all_pr_shas: Dict[int, List[str]] = {}

    print(f"\nProcessing {len(pr_list)} Pull Request objects to fetch commit SHAs...")

    for pr in pr_list:
        pr_number = pr.get('number', 'N/A')
        commits_url = pr.get('commits_url')

        if not commits_url:
            print(f"Warning: PR #{pr_number} is missing the 'commits_url' field. Skipping.")
            continue

        print(f"  Fetching commits for PR #{pr_number} from: {commits_url}")
        
        # Use the existing helper function to fetch all commit summaries for this PR
        pr_commits = _github_api_request(commits_url, github_token=github_token)

        if pr_commits is not None:
            # Extract only the SHA from each commit object
            shas = [commit.get('sha') for commit in pr_commits if commit.get('sha')]
            all_pr_shas[pr_number] = shas
            print(f"  Successfully retrieved {len(shas)} SHAs for PR #{pr_number}.")
        else:
            print(f"  Failed to retrieve commits for PR #{pr_number}. Check API logs above.")
            
    return all_pr_shas
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



if __name__ == "__main__":
    
    pr_commits = list_pr_commits(OWNER, REPO, PULL_NUMBER, GITHUB_TOKEN)

    if pr_commits:
        print(f"\n--- Found {len(pr_commits)} Commits in PR #{PULL_NUMBER} ---")
        
        # Display key information for each commit
        for i, commit in enumerate(pr_commits):
            sha = commit.get('sha', 'N/A')[:7]
            message = commit.get('commit', {}).get('message', 'No message').splitlines()[0]
            author = commit.get('commit', {}).get('author', {}).get('name', 'Unknown')
            
            print(f"  {i+1}. SHA: {sha} | Author: {author} | Message: \"{message}\"")
            
            commit_details = get_commit_by_sha(OWNER, REPO, sha, GITHUB_TOKEN)

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
                    print(f"    Patch: \n{file.get('patch', 'No patch provided')}...")

            
    else:
        print(f"\nFailed to retrieve commits for PR #{PULL_NUMBER}.")
        