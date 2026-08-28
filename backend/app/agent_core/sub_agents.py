import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent_core.schemas import (
    ExtractedStudentProfile,
    NexusCanvasProjectSpec,
)


# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)


# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# api_key may be None if .env is not set; agents will raise at call time


def extract_profile_agent(history: list) -> ExtractedStudentProfile:

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        timeout=60,
    )

    prompt = f"""
You are a student profile extraction agent for a hackathon assistant.

Analyze the following conversation history:

{history}

Extract the student's information and return it according to the
ExtractedStudentProfile schema.

Only extract information that is actually present in the conversation.
Do not invent information.
"""

    structured_llm = llm.with_structured_output(
        ExtractedStudentProfile
    )

    return structured_llm.invoke(prompt)


def generate_canvas_spec_agent(
    profile: ExtractedStudentProfile
) -> NexusCanvasProjectSpec:

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        timeout=60,
    )

    prompt = f"""
You are a hackathon project planning agent.

Based on the following student profile:

{profile.model_dump_json(indent=2)}

Generate a complete hackathon project specification.

The project should be:
- Suitable for the student's technical level
- Relevant to their academic field and interests
- Realistic to build during a hackathon
- Clearly structured
- Easy for a student team to implement

Return the result according to the NexusCanvasProjectSpec schema.
"""

    structured_llm = llm.with_structured_output(
        NexusCanvasProjectSpec
    )

    return structured_llm.invoke(prompt)