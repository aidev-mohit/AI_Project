
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from the same folder as this Python file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

# Get Gemini API key
my_api_key = os.getenv("GEMINI_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai! Check your .env file.")

# Create Gemini client
client = genai.Client(api_key=my_api_key)

# Model and prompt
model = "gemini-3.8-flash"
role = "user"
prompt = "Provide me few DSA channels names that i can study from. Make sure the channel have a good reputation and have good content. Provide me the names in a list format."

# SYSTEM instruction
message_system = (
    "You are a helpful assistant that suggests DSA channel names. "
    "The names should be well-known and reputable, and the content should be of high quality. "
)

# Send request to Gemini
response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=message_system
    )
)

# Print response
print("#" * 40)
answer = response.text
print(answer)
print("#" * 40)
