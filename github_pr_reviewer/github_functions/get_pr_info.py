import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_pr_info_from_url(pr_url):
    """
    Parses a GitHub Pull Request URL to extract OWNER, REPO, and PULL_NUMBER,
    and retrieves the GITHUB_TOKEN from the environment.
    
    Args:
        pr_url (str): The full URL of the GitHub Pull Request.
        
    Returns:
        Dict[str, Any]: A dictionary containing OWNER (str), REPO (str), 
                        PULL_NUMBER (int), and GITHUB_TOKEN (str | None).
    """
    # Use a default URL for demonstration if parsing fails
    DEFAULT_OWNER = "neha-duggirala"
    DEFAULT_REPO = "Github-issue-resolver"
    DEFAULT_PULL_NUMBER = 1 

    try:
        parsed_url = urlparse(pr_url)
        # Filter out empty strings from the path parts
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        # Expected format: [OWNER, REPO, 'pull', PULL_NUMBER]
        if len(path_parts) >= 4 and path_parts[2] == 'pull' and path_parts[3].isdigit():
            owner = path_parts[0]
            repo = path_parts[1]
            pull_number = int(path_parts[3])
        else:
            print(f"Warning: Could not parse URL path '{parsed_url.path}'. Using defaults.")
            owner, repo, pull_number = DEFAULT_OWNER, DEFAULT_REPO, DEFAULT_PULL_NUMBER
            
    except Exception as e:
        print(f"Error parsing PR URL '{pr_url}': {e}. Using defaults.")
        owner, repo, pull_number = DEFAULT_OWNER, DEFAULT_REPO, DEFAULT_PULL_NUMBER
        
    github_token = os.getenv("GITHUB_TOKEN")
    
    return {
        "OWNER": owner,
        "REPO": repo,
        "PULL_NUMBER": pull_number,
        "GITHUB_TOKEN": github_token
    }


if __name__ == "__main__":
    # Example usage
    pr_url = "https://github.com/neha-duggirala/Github-issue-resolver/pull/1"
    pr_info = get_pr_info_from_url(pr_url)
    print(pr_info)