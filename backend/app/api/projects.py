"""
projects.py
-----------
FastAPI routes for Hackathon Projects.

POST   /api/projects              — Create a new project
GET    /api/projects              — List user's projects
GET    /api/projects/{id}         — Get project details + stage data
PATCH  /api/projects/{id}         — Update project metadata or advance stage
DELETE /api/projects/{id}         — Delete a project
"""

import json
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import HackathonProject, StageData, User
from app.agent_core.hackathon_agents import STAGE_ORDER, STAGE_LABELS
from app.agent_core.hackathon_orchestrator import calculate_progress

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)


# =========================================================
# Schemas
# =========================================================

class CreateProjectRequest(BaseModel):
    project_name: str
    hackathon_name: Optional[str] = None
    theme: Optional[str] = None
    interests: Optional[str] = None
    skills: Optional[str] = None
    team_info: Optional[str] = None
    constraints: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    project_name: Optional[str] = None
    hackathon_name: Optional[str] = None
    theme: Optional[str] = None
    interests: Optional[str] = None
    skills: Optional[str] = None
    team_info: Optional[str] = None
    constraints: Optional[str] = None
    current_stage: Optional[str] = None


def _stage_summary(stage_row: StageData) -> dict:
    ai_outputs = None
    if stage_row.ai_outputs:
        try:
            ai_outputs = json.loads(stage_row.ai_outputs)
        except json.JSONDecodeError:
            ai_outputs = {"last_response": stage_row.ai_outputs}

    return {
        "id": stage_row.id,
        "stage": stage_row.stage,
        "stage_label": STAGE_LABELS.get(stage_row.stage, stage_row.stage),
        "status": stage_row.status,
        "ai_outputs": ai_outputs,
        "updated_at": stage_row.updated_at,
    }


def _project_response(project: HackathonProject) -> dict:
    stage_map = {s.stage: _stage_summary(s) for s in project.stages}

    stages_full = []
    for stage_key in STAGE_ORDER:
        if stage_key in stage_map:
            stages_full.append(stage_map[stage_key])
        else:
            stages_full.append({
                "stage": stage_key,
                "stage_label": STAGE_LABELS.get(stage_key, stage_key),
                "status": "pending",
                "ai_outputs": None,
                "updated_at": None,
            })

    return {
        "id": project.id,
        "project_name": project.project_name,
        "hackathon_name": project.hackathon_name,
        "theme": project.theme,
        "interests": project.interests,
        "skills": project.skills,
        "team_info": project.team_info,
        "constraints": project.constraints,
        "current_stage": project.current_stage,
        "current_stage_label": STAGE_LABELS.get(project.current_stage, project.current_stage),
        "progress": project.progress,
        "stages": stages_full,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


# =========================================================
# Routes
# =========================================================

@router.post("", status_code=201)
def create_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = HackathonProject(
        user_id=current_user.id,
        project_name=request.project_name,
        hackathon_name=request.hackathon_name,
        theme=request.theme,
        interests=request.interests,
        skills=request.skills,
        team_info=request.team_info,
        constraints=request.constraints,
        current_stage="problem_discovery",
        progress=0,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_response(project)


@router.get("")
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = (
        db.query(HackathonProject)
        .filter(HackathonProject.user_id == current_user.id)
        .order_by(HackathonProject.updated_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "project_name": p.project_name,
            "hackathon_name": p.hackathon_name,
            "current_stage": p.current_stage,
            "current_stage_label": STAGE_LABELS.get(p.current_stage, p.current_stage),
            "progress": p.progress,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in projects
    ]


@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(HackathonProject)
        .filter(
            HackathonProject.id == project_id,
            HackathonProject.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return _project_response(project)


@router.patch("/{project_id}")
def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(HackathonProject)
        .filter(
            HackathonProject.id == project_id,
            HackathonProject.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if request.project_name is not None:
        project.project_name = request.project_name
    if request.hackathon_name is not None:
        project.hackathon_name = request.hackathon_name
    if request.theme is not None:
        project.theme = request.theme
    if request.interests is not None:
        project.interests = request.interests
    if request.skills is not None:
        project.skills = request.skills
    if request.team_info is not None:
        project.team_info = request.team_info
    if request.constraints is not None:
        project.constraints = request.constraints
    if request.current_stage is not None:
        if request.current_stage not in STAGE_ORDER:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stage. Must be one of: {STAGE_ORDER}"
            )
        project.current_stage = request.current_stage

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return _project_response(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(HackathonProject)
        .filter(
            HackathonProject.id == project_id,
            HackathonProject.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
