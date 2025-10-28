import requests
import os

def list_pull_requests(owner: str, repo: str, state: str = 'all'):
    """
    Lists all Pull Requests in a specified GitHub repository.

    Args:
        owner (str): The account owner of the repository (e.g., 'octocat').
        repo (str): The name of the repository (e.g., 'Spoon-Knife').
        state (str, optional): Filter by PR state. Can be 'open', 'closed', or 'all'. Defaults to 'all'.
    
    Returns:
        list: A list of dictionaries, where each dictionary represents a Pull Request,
              or None if an error occurs.
    """
    # The base URL for the GitHub API endpoint
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    
    # Parameters for the API request, including pagination settings
    params = {
        'state': state,
        'per_page': 100,  # Max number of results per page
        'page': 1         # Starting page
    }
    
    # Headers for the API request
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Add Authorization header if a token is provided
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    all_prs = []
    
    print(f"Fetching {state} Pull Requests for {owner}/{repo}...")

    while True:
        try:
            response = requests.get(api_url, headers=headers, params=params)
            
            # Check for a successful response (status code 200)
            if response.status_code == 200:
                # Get the list of PRs from the current page
                prs = response.json()
                
                # If the list is empty, we've reached the end of the PRs
                if not prs:
                    break
                
                # Add the PRs from the current page to the main list
                all_prs.extend(prs)
                
                print(f"Fetched page {params['page']} with {len(prs)} PRs.")

                # Check if there's a 'next' link in the Link header for pagination
                # This is the standard way to handle pagination in the GitHub API
                if 'next' in response.links:
                    params['page'] += 1
                else:
                    break # No more pages
            
            else:
                print(f"Error fetching PRs. Status Code: {response.status_code}")
                print(f"Response: {response.json()}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the request: {e}")
            return None

    return all_prs

OWNER = "neha-duggirala"
REPO = "Github-issue-resolver"
github_token = os.environ["GITHUB_TOKEN"]
print(github_token)

try:
    # List all PRs, not just 'open' ones (using 'all' as per your documentation)
    pull_requests = list_pull_requests(OWNER, REPO, state='all') 

    if pull_requests is not None:
        print("\n--- Summary of Fetched Pull Requests ---")
        print(f"Total PRs found: {len(pull_requests)}")
        # print(pull_requests)
        
        # Display key information for the first few PRs
        display_limit = min(5, len(pull_requests))
        for i in range(display_limit):
            pr = pull_requests[i]
            print(f"  PR #{pr['number']} - Title: \"{pr['title']}\"")
            print(f"    State: {pr['state']}, Created: {pr['created_at'][:10]}, User: {pr['user']['login']}")
            print(f"    body: {pr['body']}\n")
            # print(f"    description: {pr['description']}\n")
            print(f"    commits_url: {pr['commits_url']}\n")
            print(f"    commits: {pr['head']['sha']}\n")

        if len(pull_requests) > 5:
            print(f"  ... and {len(pull_requests) - 5} more.")

except Exception as e:
    print(f"An unexpected error occurred: {e}")