
import os
import time
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from pypdf import PdfReader
from docx import Document


# ==========================================
# 1. GEMINI CLIENT
# ==========================================

load_dotenv()

my_api_key = os.getenv("GEMINI_API_KEY")

if not my_api_key:
    raise ValueError("API key kaha hai bhai")

client = genai.Client(api_key=my_api_key)

model = "gemini-3.8-flash"


# ==========================================
# 2. JOB DESCRIPTION
# ==========================================

job_description = """
Description

Do you want to solve real customer problems through innovative technology?
Do you enjoy working on scalable services in a collaborative team environment?
Do you want to see your code directly impact millions of customers worldwide?

At Amazon, we hire the best minds in technology to innovate and build
on behalf of our customers.

Our Software Development Engineers use modern technology to solve
complex problems.

Key job responsibilities

- Collaborate and communicate effectively with experienced teams.
- Design and develop scalable solutions using cloud-native architectures.
- Participate in code reviews and technical documentation.
- Build resilient distributed systems.
- Leverage GenAI and AI-powered development tools.
- Write clean and maintainable code.
- Work in an agile environment with CI/CD.
- Monitor, troubleshoot, and resolve production issues.

Basic Qualifications

- Experience with Java, Python, C++, C#, Go, Rust, or TypeScript.
- Experience with data structures, algorithms, or object-oriented design.
- Bachelor's degree in Computer Science or related STEM field.
- Must be 18 years of age or older.

Preferred Qualifications

- Technical internship or project experience.
- AI development tools.
- Cloud platforms, preferably AWS.
- SQL and NoSQL databases.
- Open-source contributions.
- Version control systems.
- Debugging and troubleshooting.
- SDLC understanding.
- Problem-solving and communication skills.
"""


# ==========================================
# 3. JOB DESCRIPTION STRUCTURE
# ==========================================

class JobD(BaseModel):

    role: str

    required_skills: list[str]

    preferred_skills: list[str]

    minimum_experience: float | None

    education_requirements: list[str]

    responsibilities: list[str]


# ==========================================
# 4. EXTRACT JOB DESCRIPTION
# ==========================================

system_prompt = """
You are an expert HR assistant.

Your job is to analyze job descriptions and extract
structured information from them.

Extract:

1. Job role
2. Required skills
3. Preferred skills
4. Minimum experience
5. Education requirements
6. Responsibilities

Important:

- Return only information present in the job description.
- Do not invent information.
- If minimum experience is not mentioned, return null.
- If information for a list is missing, return an empty list.
"""

user_prompt = f"""
Analyze the following job description:

{job_description}
"""

response = client.models.generate_content(
    model=model,
    contents=user_prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=JobD,
        temperature=0
    )
)

answer = response.text

print("JOB DESCRIPTION OUTPUT")
print(answer)

# Parse JSON and validate
job = JobD.model_validate_json(answer)

print("Role:", job.role)
print("Minimum Experience:", job.minimum_experience)
print("Education Requirements:", job.education_requirements)


# ==========================================
# 5. MATCH RESULT STRUCTURE
# ==========================================

class MatchResult(BaseModel):

    score: float

    details: dict


# ==========================================
# 6. EXPERIENCE STRUCTURE
# ==========================================

class Experience(BaseModel):

    company: str | None = None

    role: str | None = None

    duration: str | None = None

    description: str | None = None

    skills_used: list[str] = Field(default_factory=list)


# ==========================================
# 7. RESUME STRUCTURE
# ==========================================

class Resume(BaseModel):

    name: str | None = None

    email: str | None = None

    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = Field(default_factory=list)

    experiences: list[Experience] = Field(default_factory=list)

    education: list[str] = Field(default_factory=list)

    projects: list[str] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)


# ==========================================
# 8. FINAL RESUME SCORE
# ==========================================

def final_score(job, resume):

    prompt = f"""
    You are an HR recruiter.

    Compare the candidate's resume with the job description.

    JOB DESCRIPTION:

    {job.model_dump_json(indent=2)}

    CANDIDATE RESUME:

    {resume.model_dump_json(indent=2)}

    Return structured JSON containing:

    1. Candidate name
    2. Matching skills
    3. Missing important skills
    4. Whether experience requirement is met
    5. Overall match percentage from 0 to 100
    6. A short final verdict

    Keep the response concise and easy to read.

    Important:
    - Score must be between 0 and 100.
    - Do not invent candidate experience.
    - Evaluate only information present in the resume.
    - Consider required skills more important than preferred skills.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MatchResult,
            temperature=0
        )
    )

    result = MatchResult.model_validate_json(response.text)

    return result


# ==========================================
# 9. PARSE RESUME
# ==========================================

def parse_resume(resume_text):

    system_prompt = """
    You are an expert resume parser.

    Extract information from the resume based on its meaning,
    not only based on exact section headings.

    Different resumes may use different headings.

    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships

    These may all contain relevant experience.

    Skills may also appear in:
    - Skills section
    - Work experience
    - Internships
    - Projects

    Extract:

    - Name
    - Email
    - Phone
    - Total experience years
    - Skills
    - Experiences
    - Education
    - Projects
    - Certifications

    Important rules:

    1. Do not invent information.
    2. If a value is unavailable, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    """

    user_prompt = f"""
    Parse the following resume:

    {resume_text}
    """

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=Resume,
            temperature=0
        )
    )

    resume = Resume.model_validate_json(response.text)

    return resume


# ==========================================
# 10. READ PDF
# ==========================================

def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# 11. READ DOCX
# ==========================================

def read_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text += paragraph.text + "\n"

    for table in document.tables:

        for row in table.rows:

            for cell in row.cells:

                if cell.text.strip():

                    text += cell.text + "\n"

    return text


# ==========================================
# 12. READ RESUME
# ==========================================

def read_resume(file_path):

    if file_path.suffix.lower() == ".pdf":

        return read_pdf(file_path)

    elif file_path.suffix.lower() == ".docx":

        return read_docx(file_path)

    else:

        return None


# ==========================================
# 13. PROCESS RESUMES
# ==========================================

resume_folder = Path("resumes")

all_results = []

if not resume_folder.exists():

    raise FileNotFoundError(
        "Resumes folder nahi mila bhai"
    )


for file_path in resume_folder.iterdir():

    if file_path.suffix.lower() not in [".pdf", ".docx"]:

        continue

    print("\nProcessing:", file_path.name)

    resume_text = read_resume(file_path)

    if not resume_text:

        print("Resume text nahi mila")

        continue

    # LLM call 1: Resume parsing

    parsed_resume = parse_resume(resume_text)

    time.sleep(5)

    # LLM call 2: Resume scoring

    result = final_score(job, parsed_resume)

    time.sleep(5)

    print("Candidate:", parsed_resume.name)

    print("Score:", result.score)

    all_results.append({

        "name": parsed_resume.name,

        "score": result.score,

        "details": result.details

    })


# ==========================================
# 14. SORT CANDIDATES
# ==========================================

all_results.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)


# ==========================================
# 15. TOP 2 CANDIDATES
# ==========================================

top_2 = all_results[:2]

print("\nTOP 2 CANDIDATES")

for candidate in top_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )

    print(candidate["details"])


# ==========================================
# 16. LOWEST 2 CANDIDATES
# ==========================================

worst_2 = all_results[-2:]

print("\nLOWEST 2 CANDIDATES")

for candidate in worst_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )

    print(candidate["details"])
