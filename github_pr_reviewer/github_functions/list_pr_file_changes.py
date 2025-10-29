import requests
from typing import List, Dict, Any
from google.genai import types
import os

github_token = os.environ["GITHUB_TOKEN"]

def list_pr_file_changes(
    owner: str,
    repo: str,
    pull_number: int,
) -> List[Dict[str, Any]]:
    """
    Lists all files changed in a GitHub Pull Request, including the file's status
    and the actual diff content (patch).

    Args:
        owner (str): The account owner of the repository (e.g., 'octocat').
        repo (str): The name of the repository (e.g., 'Hello-World').
        pull_number (int): The number that identifies the pull request.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing
                              'filename', 'status', and 'patch'.
    """
    BASE_URL = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    all_file_changes = []
    page = 1
    per_page = 100 # Maximum allowed by the API

    print(f"Fetching file changes (patch data) for {owner}/{repo} PR #{pull_number}...")

    while True:
        params = {
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            files_data = response.json()
            
            # Stop if no files are returned (last page)
            if not files_data:
                break

            # Process files on the current page
            for file in files_data:
                # Extract filename, status, and the patch content
                all_file_changes.append({
                    "filename": file.get("filename"),
                    "status": file.get("status"),
                    "patch": file.get("patch")
                })
            
            # Prepare for the next page
            page += 1
        
        # --- Error Handling (omitted for brevity in the final output, but remains in the full code) ---
        elif response.status_code == 404:
            print(f"Error 404: PR or repository not found.")
            break
        else:
            print(f"Error {response.status_code}: Failed to fetch PR files.")
            break

    return all_file_changes

def get_pr_file_changes(owner, repo, pull_number) -> List[Dict[str, Any]]:
    """
    Extracts and returns the list of file changes with their patches from the provided changes data.

    Args:
        changes (List[Dict[str, Any]]): The list of file changes data.
        
    """
    changes = list_pr_file_changes(owner, repo, pull_number)
    output = []
    if changes:
        output.append("\n--- PR File Changes (Patch/Diff) --- \n + represent additions and - represents deletions:\n")
        for file in changes:
            output.append(f"**File:** {file['filename']} \n **Status:** {file['status']}")
            
            # The 'patch' field contains the actual diff lines
            patch_content = file['patch']
            
            if patch_content:
                output.append("\n**Patch Content (Unified Diff):**")
                # Display the patch content
                output.append(patch_content)
            elif file['status'] == 'added':
                output.append("\n**Note:** 'added' files might not always have a patch, but the full content can be fetched separately.")
            else:
                output.append("\nNo patch content found for this file.")
        
        output.append(f"Total Files Processed: {len(changes)}")
        output.append("The patch content above shows the line-by-line additions (+) and deletions (-).")
    else:
        output.append("No file changes retrieved or an error occurred.")
        
    return "\n".join(output)

schema_get_pr_file_changes = types.FunctionDeclaration(
    name="get_pr_file_changes",
    description="Lists all files changed in a GitHub Pull Request, including the file's status and the actual diff content (patch). additions and deletions are represented with + and - respectively.",
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

if __name__ == '__main__':
    # ⚠️ Replace these with your actual details
    OWNER = "neha-duggirala"
    REPO = "Github-issue-resolver"
    PULL_NUMBER = 9 # A public, sample PR number
    print(get_pr_file_changes(OWNER, REPO, PULL_NUMBER))
    