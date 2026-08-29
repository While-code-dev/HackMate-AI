import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.agent_core.schemas import (
    ExtractedStudentProfile,
    NexusCanvasProjectSpec,
)


BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")


def _get_llm():
    current_api_key = os.getenv("GROQ_API_KEY") or api_key

    if not current_api_key:
        raise RuntimeError(
            f"GROQ_API_KEY is not configured. Check your .env file at: {env_path}"
        )

    return ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=current_api_key,
        temperature=0.3,
        timeout=60,
    )


def extract_profile_agent(history: list) -> ExtractedStudentProfile:

    llm = _get_llm()

    prompt = f"""
You are a student profile extraction agent for a hackathon assistant.

Analyze the following conversation history:

{history}

Extract the student's information and return it according to the
ExtractedStudentProfile schema.

Only extract information that is actually present in the conversation.

Do not invent, assume, or infer personal information that the student
did not provide.

Preserve the meaning of the student's responses.

If information is missing, leave the corresponding schema field empty
or use its default value.

Return only information supported by the conversation.
"""

    structured_llm = llm.with_structured_output(
        ExtractedStudentProfile
    )

    return structured_llm.invoke(prompt)


def generate_canvas_spec_agent(
    profile: ExtractedStudentProfile
) -> NexusCanvasProjectSpec:

    llm = _get_llm()

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
- Practical for a student team to implement
- Specific enough to guide development
- Flexible enough to allow the team to adapt the idea

Do not invent personal information about the student.

Use the student's actual profile as the foundation.

Return the result according to the NexusCanvasProjectSpec schema.
"""

    structured_llm = llm.with_structured_output(
        NexusCanvasProjectSpec
    )

    return structured_llm.invoke(prompt)