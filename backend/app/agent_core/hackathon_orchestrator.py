"""
hackathon_orchestrator.py
--------------------------
Central orchestrator for the HackMate hackathon journey.

Routes user messages to the correct specialized agent based on the
current hackathon stage, builds project context from saved stage outputs,
and returns structured responses.
"""

import json
from typing import Optional

from app.agent_core.hackathon_agents import AGENT_MAP, STAGE_ORDER, STAGE_LABELS


def build_project_context(project, stage_data_list: list) -> dict:
    """
    Build a unified project context dict from a HackathonProject row
    and its associated StageData rows.
    """
    ctx = {
        "project_name": project.project_name,
        "hackathon_name": project.hackathon_name,
        "theme": project.theme,
        "interests": project.interests,
        "skills": project.skills,
        "team_info": project.team_info,
        "constraints": project.constraints,
        "current_stage": project.current_stage,
        "stage_outputs": {},
    }

    for stage_row in stage_data_list:
        if stage_row.ai_outputs:
            try:
                outputs = json.loads(stage_row.ai_outputs)
                ctx["stage_outputs"][stage_row.stage] = outputs.get("last_response", "")
            except (json.JSONDecodeError, AttributeError):
                ctx["stage_outputs"][stage_row.stage] = stage_row.ai_outputs

    return ctx


def route_to_agent(
    stage: str,
    user_message: str,
    project_ctx: dict,
    chat_history: list,
) -> str:
    """
    Route the user message to the specialized agent for the given stage.
    Falls back to a generic response if the stage is unknown.
    """
    agent_fn = AGENT_MAP.get(stage)

    if agent_fn is None:
        # Fallback: general hackathon assistant
        from app.agent_core.hackathon_agents import _llm
        fallback = _llm()
        response = fallback.invoke(
            f"You are HackMate AI, a hackathon copilot. "
            f"Help the user with: {user_message}"
        )
        return response.content

    return agent_fn(user_message, project_ctx, chat_history)


def calculate_progress(stage_data_list: list) -> int:
    """
    Calculate project progress as a percentage based on completed stages.
    """
    if not stage_data_list:
        return 0

    completed = sum(
        1 for s in stage_data_list
        if s.status == "completed"
    )

    total = len(STAGE_ORDER)
    return min(100, int((completed / total) * 100))


def get_next_stage(current_stage: str) -> Optional[str]:
    """Return the next stage after the current one, or None if at the end."""
    try:
        idx = STAGE_ORDER.index(current_stage)
        if idx < len(STAGE_ORDER) - 1:
            return STAGE_ORDER[idx + 1]
    except ValueError:
        pass
    return None


def get_stage_label(stage: str) -> str:
    """Human-readable label for a stage key."""
    return STAGE_LABELS.get(stage, stage.replace("_", " ").title())
