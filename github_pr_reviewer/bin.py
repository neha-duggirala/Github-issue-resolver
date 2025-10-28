import os
from google.genai import types
from google import genai

model = os.environ["MODEL"]
api_key = os.environ["GOOGLE_API_KEY"]


client = genai.Client(api_key= api_key)
response = client.models.generate_content(
    model=model,
    contents=[
       types.Content(role="user", parts =[types.Part(text="Hello, who are you!")])
    ],
)
print("Response:", response.text)