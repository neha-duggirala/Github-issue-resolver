
import json
from typing import Any, Dict, Optional
import requests



def _github_api_post_request(url: str, data: Dict[str, Any], github_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Helper function to make a POST request to the GitHub API (e.g., for creation).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 201: # 201 Created is the expected status code for successful POST
            return response.json()
        else:
            error_message = response.json().get('message', 'No error message provided.')
            print(f"Error POSTing data to {url}. Status Code: {response.status_code}")
            print(f"GitHub Message: {error_message}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the POST request to {url}: {e}")
        return None

def create_pr_review_comment(
    owner: str, 
    repo: str, 
    pull_number: int, 
    body: str, 
    github_token: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Creates a new PR review comment on a specific line of the diff using the GitHub API (POST method).
    
    Args:
        owner (str): The repository owner.
        repo (str): The repository name.
        pull_number (int): The number that identifies the pull request.
        body (str): The text content for the new comment.
       
        github_token (Optional[str]): GitHub Personal Access Token with 'pull requests' write permission.
        
    Returns:
        Optional[Dict[str, Any]]: The created comment object (dictionary), or None on error.
    """
    if not github_token:
        print("ERROR: GITHUB_TOKEN is required for this operation (POST).")
        return None
        
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
    data = {
        "body": body,
       
    }

    print(f"Attempting to create a review comment on PR #{pull_number} in {owner}/{repo}...")
    
    new_comment = _github_api_post_request(api_url, data, github_token)
    
    if new_comment:
        print(f"SUCCESS: New comment created with ID {new_comment.get('id')}.")
    
    return new_comment

if __name__ == "__main__":
    
    PR_URL = "https://github.com/neha-duggirala/Github-issue-resolver/pull/1"
    import os
    from dotenv import load_dotenv

    load_dotenv()
    OWNER = "neha-duggirala"
    REPO = "Github-issue-resolver"
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    PULL_NUMBER = 1
    NEW_COMMENT_BODY = '''
*   **Integrate Setup Commands**: Consider moving the commands from `commands.txt` into the `readme.md` under a new section like "Development Setup" or "Installation". This keeps all essential project information consolidated. If the project grows, a `CONTRIBUTING.md` could be a good home for more detailed developer instructions.
*   **Correct Typos and Paths**: Please correct the typo and path in `commands.txt` from `.venv\Scripts ctivate.bat` to `.venv\Scripts\Activate.bat`.
*   **Add Trailing Newline**: Ensure `commands.txt` (if it remains) has a trailing newline.
*   **Clarify README Origin**: If the README was manually created as the *initial* version, a commit message like "feat: Add initial README" might be more descriptive. If it truly was auto-generated, no change is needed, but it's good to confirm.        
*   **Specify OS Context**: The `commands.txt` uses `.ps1` and `.bat` files, indicating Windows-specific commands. It would be helpful to explicitly state this or provide alternatives for other operating systems (e.g., Linux/macOS using `source .venv/bin/activate`).
'''
    updated_comment_response = create_pr_review_comment(OWNER, REPO, PULL_NUMBER, NEW_COMMENT_BODY, GITHUB_TOKEN)
    