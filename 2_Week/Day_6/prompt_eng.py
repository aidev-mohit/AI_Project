
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================
# GEMINI API SETUP
# =========================

load_dotenv(Path(__file__).resolve().parent / ".env")

my_api_key = os.getenv("GEMINI_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = genai.Client(api_key=my_api_key)

model = "gemini-3.8-flash"


# =========================
# LLM FUNCTION
# =========================

def llm_ans(prompt):

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2
        )
    )

    ans = response.text

    return ans


# =========================
# USER PROMPT
# =========================

bad_prompt = """
#Role: You are a customer support agent. You will be given a user complaint. Your task is to classify the complaint into one of the following categories: "Technical Issue", "Billing Issue", "Account Issue", "Feedback", or "Other".

This is a user complaint:
My laptop is not working.
Classify this complaint.
"""

print(llm_ans(bad_prompt))
