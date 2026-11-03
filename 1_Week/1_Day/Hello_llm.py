
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv(r"C:\Users\Asus\AI_Project\.env")

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found in .env file!")

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send prompt to Gemini
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explain AI in simple words with an example."
)

# Print response
print("=" * 50)
print(response.text)
print("=" * 50)
