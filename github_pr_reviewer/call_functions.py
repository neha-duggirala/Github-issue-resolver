from google.genai import types
from github_functions.get_pr_info import schema_get_pr_info, get_pr_info_from_url
from github_functions.pr_commits import schema_get_pr_commit_details, get_pr_commit_details
from github_functions.add_pr_comment import schema_add_pr_comment, create_pr_review_comment 
from github_functions.list_pr_file_changes import schema_get_pr_file_changes, get_pr_file_changes

available_functions = types.Tool(
    function_declarations=[
        schema_get_pr_info,
        schema_get_pr_commit_details,
        schema_add_pr_comment,
        schema_get_pr_file_changes
    ]
)

def call_function(function_call_part, verbose=False):
    if verbose:
        print(
            f" - Calling function: {function_call_part.name}({function_call_part.args})"
        )
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_map = {
        "get_pr_info_from_url": get_pr_info_from_url,
        "get_pr_commit_details": get_pr_commit_details,
        "create_pr_review_comment": create_pr_review_comment,
        "get_pr_file_changes": get_pr_file_changes
    }
    function_name = function_call_part.name
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    args = dict(function_call_part.args)
    function_result = function_map[function_name](**args)
    # print(f"using tools: {function_result}")
    
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )