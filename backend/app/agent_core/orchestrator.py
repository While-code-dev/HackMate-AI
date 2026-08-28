import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent_core.sub_agents import (
    extract_profile_agent,
    generate_canvas_spec_agent,
)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)


# --------------------------------------------------
# Gemini API key
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


# --------------------------------------------------
# Master Orchestrator (legacy — kept for backward compat)
# --------------------------------------------------

class MasterOrchestrator:

    def __init__(self):

        if not api_key:
            raise ValueError(
                f"Gemini API key not found. Check your .env file at: {env_path}"
            )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key,
            timeout=120,
        )

    def process_message(
        self,
        user_message: str,
        history: list,
    ) -> dict:

        # Add current user message to history
        full_history = history + [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        # ------------------------------------------
        # Extract student profile
        # ------------------------------------------

        profile = extract_profile_agent(full_history)

        # ------------------------------------------
        # Check missing information
        # ------------------------------------------

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

        # ------------------------------------------
        # Ask for missing information
        # ------------------------------------------

        if missing:

            prompt = (
                "The user is asking about hackathon ideas. "
                "Briefly and naturally ask them about: "
                + ", ".join(missing)
                + "."
            )

            response = self.llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = "".join(
                    b.get("text", "") if isinstance(b, dict) else str(b)
                    for b in content
                )

            return {
                "chat_reply": content,
                "is_ready_for_spec": False,
                "project_spec": None,
            }

        # ------------------------------------------
        # Generate project specification
        # ------------------------------------------

        canvas_spec = generate_canvas_spec_agent(profile)

        return {
            "chat_reply": (
                f"I've generated your visual hackathon blueprint "
                f"for '{canvas_spec.project_title}'!"
            ),
            "is_ready_for_spec": True,
            "project_spec": canvas_spec.model_dump(),
        }
