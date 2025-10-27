import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from prompts import *
import os 
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("MODEL")


def google_client():
    client = genai.Client(api_key= api_key)

        
    question = user_prompt
    messages = [
        types.Content(role="user", parts =[types.Part(text=question)])
    ]

    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                # max_output_tokens=1024,
            ),
    )

    if response.usage_metadata:
        print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Generation Tokens: {response.usage_metadata.candidates_token_count}")
        
    return response.text


print(google_client())
