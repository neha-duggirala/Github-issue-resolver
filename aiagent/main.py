import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from prompts import system_prompt
from call_functions import available_functions, call_function

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("MODEL")


def google_client():
    client = genai.Client(api_key=api_key)
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)
    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?" --verbose')
        sys.exit(1)
        
    user_prompt = " ".join(args)
    
    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    max_iters = 20
    for i in range(max_iters):

        response = client.models.generate_content(
            model=model,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[available_functions],
                max_output_tokens=1024,
            ),
        )
        
        if response is None:
            print("No response from the model.")
            return None

        if response.usage_metadata:
            print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Generation Tokens: {response.usage_metadata.candidates_token_count}")
        if response.candidates:
            for candidate in response.candidates:
                if candidate == None:
                    continue
                messages.append(candidate.content)
                
        if response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose)
                # print(function_call_result)
                
                if (
                    not function_call_result.parts
                    or not function_call_result.parts[0].function_response
                ):
                    raise Exception("empty function call result")
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")
                messages.append(function_call_result)
        else:
            print("Final Function call")
            return response.text


print(google_client())
