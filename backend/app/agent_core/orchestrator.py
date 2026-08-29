import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.agent_core.sub_agents import (
    extract_profile_agent,
    generate_canvas_spec_agent,
)


BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")


class MasterOrchestrator:

    def __init__(self):

        current_api_key = os.getenv("GROQ_API_KEY") or api_key

        if not current_api_key:
            raise ValueError(
                f"Groq API key not found. Check your .env file at: {env_path}"
            )

        self.llm = ChatGroq(
            model="openai/gpt-oss-20b",
            groq_api_key=current_api_key,
            temperature=0.7,
            timeout=120,
        )

    def process_message(
        self,
        user_message: str,
        history: list,
    ) -> dict:

        full_history = history + [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        profile = extract_profile_agent(full_history)

        missing = []

        if not profile.academic_field and not profile.interests:
            missing.append(
                "your study field or technical interests"
            )

        if not profile.tech_level:
            missing.append(
                "your technical experience level "
                "(Beginner, Intermediate, or Advanced)"
            )

        if missing:

            prompt = f"""You are the HackMate AI Master Orchestrator.

Have a natural conversation with the user about their hackathon project.

The user has not provided enough information yet.

You need to naturally ask about:
{", ".join(missing)}

Do not use a rigid questionnaire.

Do not ask unnecessary questions.

Use the existing conversation context.

If the user has already answered part of this information, do not ask for it again.

Respond naturally like a modern conversational AI assistant.

Conversation:
{full_history}
"""

            response = self.llm.invoke(prompt)

            content = response.content

            if isinstance(content, list):
                content = "".join(
                    block.get("text", "")
                    if isinstance(block, dict)
                    else str(block)
                    for block in content
                )

            return {
                "chat_reply": content,
                "is_ready_for_spec": False,
                "project_spec": None,
            }

        canvas_spec = generate_canvas_spec_agent(profile)

        return {
            "chat_reply": (
                f"I've generated your visual hackathon blueprint "
                f"for '{canvas_spec.project_title}'!"
            ),
            "is_ready_for_spec": True,
            "project_spec": canvas_spec.model_dump(),
        }