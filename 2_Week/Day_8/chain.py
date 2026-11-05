import os
from pathlib import Path
import re
import time

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

JD = """
We are hiring a Backend Python Developer.

Requirements:
- Strong Python
- FastAPI or Django
- PostgreSQL
- Docker
- AWS
- REST APIs
- 2+ years of experience
"""

RESUME="""
Name: Rahul Sharma

Experience:
3 years as a Software Developer.

Skills:
Python, FastAPI, MySQL, Docker,
REST APIs, Git

Projects:
Built a food delivery backend using
FastAPI and MySQL.

Deployed applications using Docker.
"""


def ask_llm(system_prompt, user_prompt):

    prompt = f"""
    System Instructions:
    {system_prompt}

    User:
    {user_prompt}
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    answer = response.text

    return answer

def step1_res_extract(RESUME):
    print("STEP 1")
    system_prompt="""
    You are a professional HR assistant. Extract the skills from the candidates resume provided.
    Only return the skills no other information. Do not invent any skillsby yourself.
    Output Format:
    Skills should be separated by commas. Just return comma separated skills do not return any other filler information
    """
    user_prompt=f"""
    Extract the skills from this resume
    {RESUME}
    """
    return ask_llm(system_prompt, user_prompt)

def step2_JD_extract(JD):
    print("step2")
    system_prompt="""
    You are a professional HR assistant. Extract the skills from the Job description  provided.
    Only return the skills no other information. Do not invent any skills by yourself.
    Output Format:
    Skills should be separated by commas. Just return comma separated skills do not return any other filler information
    """
    user_prompt=f"""
    Extract the skills from this JD
    {JD}
    """
    return ask_llm(system_prompt, user_prompt)

def step3_match(candidate,jd):
    print("step3")
    system_prompt="""
    You are a professional HR assistant. compare the skills of candidate and the skills required in the JD and produce a final score between
    1 and 100. also produce a short verdict whther the candidate is a good fit for the role.
    """
    user_prompt=f"""
    Compare and matc h the skills
    JD:
    {jd}
    Candidate:
    {candidate}
    """
    return ask_llm(system_prompt, user_prompt)

candidate=step1_res_extract(RESUME)
print(candidate)
time.sleep(2)
jd=step2_JD_extract(JD)
print(jd)
time.sleep(2)
score=step3_match(candidate,jd)
print(score)