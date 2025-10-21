import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os 
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("MODEL")


def google_client():
    client = genai.Client(api_key= api_key)
    if len(sys.argv) < 2:
        print("Usage: uv run main.py '<Your Question>'")
        sys.exit(1)
        
    question = sys.argv[1]
    messages = [
        types.Content(role="user", parts =[types.Part(text=question)])
    ]

    response = client.models.generate_content(
        model=model,
        contents=messages,
    )

    if response.usage_metadata:
        print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Generation Tokens: {response.usage_metadata.candidates_token_count}")
        
    return response.text


print(google_client())
