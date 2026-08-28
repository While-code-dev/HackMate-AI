"""
stages.py
---------
FastAPI routes for Hackathon Stage interactions.

POST /api/projects/{id}/stages/{stage}/chat     — Send message to the stage agent
GET  /api/projects/{id}/stages/{stage}          — Get stage data (history + outputs)
POST /api/projects/{id}/stages/{stage}/complete — Mark stage as completed + advance
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import HackathonProject, StageData, User
from app.agent_core.hackathon_agents import STAGE_ORDER, STAGE_LABELS
from app.agent_core.hackathon_orchestrator import (
    build_project_context,
    route_to_agent,
    calculate_progress,
    get_next_stage,
)

router = APIRouter(
    prefix="/api/projects",
    tags=["Stages"],
)


# =========================================================
# Schemas
# =========================================================

class StageChatRequest(BaseModel):
    message: str


class StageCompleteRequest(BaseModel):
    advance: bool = True  # Whether to move to the next stage


# =========================================================
# Helpers
# =========================================================

def _get_project_or_404(
    project_id: int,
    user_id: int,
    db: Session,
) -> HackathonProject:
    project = (
        db.query(HackathonProject)
        .filter(
            HackathonProject.id == project_id,
            HackathonProject.user_id == user_id,
        )
        .first()
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_or_create_stage(
    project_id: int,
    stage: str,
    db: Session,
) -> StageData:
    stage_row = (
        db.query(StageData)
        .filter(
            StageData.project_id == project_id,
            StageData.stage == stage,
        )
        .first()
    )

    if stage_row is None:
        stage_row = StageData(
            project_id=project_id,
            stage=stage,
            status="in_progress",
            chat_history=json.dumps([]),
            ai_outputs=json.dumps({}),
        )
        db.add(stage_row)
        db.commit()
        db.refresh(stage_row)

    return stage_row


# =========================================================
# Routes
# =========================================================

@router.post("/{project_id}/stages/{stage}/chat")
def stage_chat(
    project_id: int,
    stage: str,
    request: StageChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the specialized agent for this stage."""

    if stage not in STAGE_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage. Must be one of: {STAGE_ORDER}"
        )

    project = _get_project_or_404(project_id, current_user.id, db)

    # Load all stage data for context building
    all_stages = (
        db.query(StageData)
        .filter(StageData.project_id == project_id)
        .all()
    )

    # Build unified project context
    project_ctx = build_project_context(project, all_stages)

    # Get or create this stage's row
    stage_row = _get_or_create_stage(project_id, stage, db)

    # Load chat history
    try:
        chat_history = json.loads(stage_row.chat_history or "[]")
    except json.JSONDecodeError:
        chat_history = []

    # Invoke the specialized agent
    try:
        ai_response = route_to_agent(
            stage=stage,
            user_message=request.message,
            project_ctx=project_ctx,
            chat_history=chat_history,
        )
    except Exception as exc:
        # Never crash the endpoint on AI errors
        ai_response = (
            "I apologize — I encountered an error processing your request. "
            f"Please try again. (Error: {type(exc).__name__})"
        )

    # Append to chat history
    chat_history.append({"role": "user", "content": request.message})
    chat_history.append({"role": "assistant", "content": ai_response})

    # Save last AI response in ai_outputs
    try:
        ai_outputs = json.loads(stage_row.ai_outputs or "{}")
    except json.JSONDecodeError:
        ai_outputs = {}

    ai_outputs["last_response"] = ai_response
    ai_outputs["last_updated"] = datetime.utcnow().isoformat()

    # Update stage row
    stage_row.chat_history = json.dumps(chat_history)
    stage_row.ai_outputs = json.dumps(ai_outputs)
    stage_row.status = "in_progress"
    stage_row.updated_at = datetime.utcnow()

    db.commit()

    # Recalculate progress
    all_stages_refreshed = (
        db.query(StageData)
        .filter(StageData.project_id == project_id)
        .all()
    )
    project.progress = calculate_progress(all_stages_refreshed)
    project.updated_at = datetime.utcnow()
    db.commit()

    return {
        "stage": stage,
        "stage_label": STAGE_LABELS.get(stage, stage),
        "ai_response": ai_response,
        "message_count": len(chat_history),
    }


@router.get("/{project_id}/stages/{stage}")
def get_stage(
    project_id: int,
    stage: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the stage data including chat history and AI outputs."""

    if stage not in STAGE_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage. Must be one of: {STAGE_ORDER}"
        )

    project = _get_project_or_404(project_id, current_user.id, db)

    stage_row = (
        db.query(StageData)
        .filter(
            StageData.project_id == project_id,
            StageData.stage == stage,
        )
        .first()
    )

    if stage_row is None:
        return {
            "stage": stage,
            "stage_label": STAGE_LABELS.get(stage, stage),
            "status": "pending",
            "chat_history": [],
            "ai_outputs": None,
        }

    try:
        chat_history = json.loads(stage_row.chat_history or "[]")
    except json.JSONDecodeError:
        chat_history = []

    try:
        ai_outputs = json.loads(stage_row.ai_outputs or "{}")
    except json.JSONDecodeError:
        ai_outputs = {}

    return {
        "stage": stage,
        "stage_label": STAGE_LABELS.get(stage, stage),
        "status": stage_row.status,
        "chat_history": chat_history,
        "ai_outputs": ai_outputs,
        "updated_at": stage_row.updated_at,
    }


@router.post("/{project_id}/stages/{stage}/complete")
def complete_stage(
    project_id: int,
    stage: str,
    request: StageCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a stage as completed and optionally advance to the next stage."""

    if stage not in STAGE_ORDER:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage. Must be one of: {STAGE_ORDER}"
        )

    project = _get_project_or_404(project_id, current_user.id, db)

    stage_row = _get_or_create_stage(project_id, stage, db)
    stage_row.status = "completed"
    stage_row.updated_at = datetime.utcnow()

    # Advance to next stage if requested
    next_stage = None
    if request.advance:
        next_stage = get_next_stage(stage)
        if next_stage:
            project.current_stage = next_stage

    # Recalculate progress
    all_stages = (
        db.query(StageData)
        .filter(StageData.project_id == project_id)
        .all()
    )
    project.progress = calculate_progress(all_stages)
    project.updated_at = datetime.utcnow()

    db.commit()

    return {
        "stage": stage,
        "stage_label": STAGE_LABELS.get(stage, stage),
        "status": "completed",
        "next_stage": next_stage,
        "next_stage_label": STAGE_LABELS.get(next_stage, next_stage) if next_stage else None,
        "project_progress": project.progress,
    }
