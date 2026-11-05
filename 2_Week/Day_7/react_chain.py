
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


# =========================
# TOOLS
# =========================

def get_product(product):

    product = product.lower().strip()

    if product == "iphone 17":
        return 1000

    elif product == "iphone 15":
        return 800

    else:
        return 0


def calculator(expression):

    try:
        # Only allow basic arithmetic characters
        if not re.fullmatch(r"[0-9+\-*/().\s]+", expression):
            return "Invalid expression"

        return eval(expression)

    except Exception:
        return "Invalid expression"


tools = {
    "get_product": get_product,
    "calculator": calculator
}


# =========================
# SYSTEM PROMPT
# =========================

system_prompt = """
You are a shopping assistant.

You have these tools:

get_product(product)
calculator(expression)

IMPORTANT:
Call tools exactly like these examples:

Action: get_product("iphone 17")
Action: calculator("5000 - 1000")

Never write:
get_product(product="iphone 17")

Never write:
calculator(expression="5000 - 1000")

Follow these rules:

1. Decide what you need to do next.
2. Call ONLY ONE tool at a time.
3. After writing an Action, STOP immediately.
4. Never guess or invent a tool result.
5. Wait until you receive an Observation.
6. Then decide your next action.
7. When the task is complete, give the Final Answer.

Format:

Thought: what you need to do
Action: tool_name("argument")

When finished:

Final Answer: your answer
"""


# =========================
# REACT AGENT
# =========================

def run_agent(question):

    conversation = system_prompt + "\n\nUser: " + question

    for step in range(5):

        print("\n------------------")
        print("STEP", step + 1)
        print("------------------")

        response = client.models.generate_content(
            model=model,
            contents=conversation,
            config=types.GenerateContentConfig(
                temperature=0
            )
        )

        answer = response.text

        print(answer)

        # Agent has finished
        if "Final Answer:" in answer:
            break

        # Find Action
        match = re.search(
            r'Action:\s*(\w+)\("([^"]*)"\)',
            answer
        )

        if not match:

            print("No valid Action found.")
            break

        tool_name = match.group(1)

        tool_input = match.group(2)

        # Run tool
        if tool_name in tools:

            tool = tools[tool_name]

            observation = tool(tool_input)

        else:

            observation = "Tool not found"

        print("Observation:", observation)

        # Add assistant response and tool observation
        conversation += "\n\nAssistant: " + answer

        conversation += (
            "\n\nObservation: "
            + str(observation)
        )

        time.sleep(2)


# =========================
# USER PROMPT
# =========================

prompt = """
I have 5000 rupees.
What is the price of an iphone 17?
And how much money will I have left?
"""

run_agent(prompt)
