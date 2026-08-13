"""
bob.py
------
FastAPI router for the IBM Bob scaffold endpoint.

POST /api/bob/scaffold
  Accepts a project_spec payload, optionally persists it against an existing
  conversation, invokes IBM Bob in headless mode, and returns the result.
"""

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Conversation, User
from app.services.bob_runner import run_bob_scaffold


router = APIRouter(
    prefix="/api/bob",
    tags=["Bob Scaffold"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class BobScaffoldRequest(BaseModel):
    """Payload for triggering Bob's scaffold generation."""

    project_spec: dict[str, Any]
    """Arbitrary project specification (NexusCanvasProjectSpec-shaped or free-form)."""

    conversation_id: int | None = None
    """Optional: attach the spec to an existing conversation record."""


class BobScaffoldResponse(BaseModel):
    """Response returned after Bob completes (or fails)."""

    status: str
    """'success' | 'error' | 'timeout'"""

    output: str
    """Raw stdout from Bob."""

    error: str
    """Stderr / error description (empty string when none)."""

    exit_code: int | None
    """Bob process exit code, or None if it never started / timed out."""

    conversation_id: int | None = None
    """Echoed back if a conversation was supplied."""


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/scaffold", response_model=BobScaffoldResponse)
def bob_scaffold(
    request: BobScaffoldRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BobScaffoldResponse:
    """Invoke IBM Bob in headless mode with the supplied *project_spec*.

    If *conversation_id* is provided the project_spec is persisted against
    that conversation's ``project_spec`` column so it can be retrieved later.
    """

    # ------------------------------------------------------------------
    # 1. Optionally attach spec to an existing conversation
    # ------------------------------------------------------------------
    if request.conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Persist spec on conversation if the column exists
        if hasattr(conversation, "project_spec"):
            import json
            conversation.project_spec = json.dumps(request.project_spec)
            db.commit()

    # ------------------------------------------------------------------
    # 2. Guard: BOB_API_KEY must be configured
    # ------------------------------------------------------------------
    if not os.getenv("BOB_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail=(
                "BOB_API_KEY is not configured. "
                "Set it in your environment before calling this endpoint."
            ),
        )

    # ------------------------------------------------------------------
    # 3. Run Bob
    # ------------------------------------------------------------------
    bob_result = run_bob_scaffold(request.project_spec)

    # ------------------------------------------------------------------
    # 4. Return structured response (never raise on Bob errors –
    #    callers inspect the status field instead)
    # ------------------------------------------------------------------
    return BobScaffoldResponse(
        status=bob_result["status"],
        output=bob_result["output"],
        error=bob_result["error"],
        exit_code=bob_result["exit_code"],
        conversation_id=request.conversation_id,
    )
