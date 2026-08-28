"""
tests/test_hackmate.py
----------------------
Automated test suite for HackMate AI backend.

Uses a file-based SQLite test database (test_hackmate.db) so it's
independent of the production database.

Run from the backend/ directory:
    pytest tests/test_hackmate.py -v
"""

import json
import os
import sys
import uuid
from pathlib import Path

# Ensure app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure test environment BEFORE importing any app modules
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-tests-only"
os.environ["GEMINI_API_KEY"] = "test-fake-key"
os.environ["DATABASE_URL"] = "sqlite:///./test_hackmate.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# =========================================================
# IMPORTANT: Override the database engine BEFORE importing app
# =========================================================

import app.database as _db_module

TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test_hackmate.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Patch BEFORE create_all runs in main.py
_db_module.engine = _test_engine
_db_module.SessionLocal = _TestSessionLocal


def _override_get_db():
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Now import app (this will call create_all on the patched test engine)
from app.database import Base, get_db
from app.main import app

Base.metadata.create_all(bind=_test_engine)
app.dependency_overrides[get_db] = _override_get_db

client = TestClient(app)


def pytest_sessionfinish(session, exitstatus):
    """Clean up test database after test run."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


# =========================================================
# Helpers
# =========================================================

def register_and_login(username: str, password: str = "testpass123") -> dict:
    """Register a new user and return login response data."""
    client.post("/api/auth/register", json={"username": username, "password": password})
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed: {res.json()}"
    return res.json()


def auth_headers(username: str) -> dict:
    data = register_and_login(username)
    return {"Authorization": f"Bearer {data['access_token']}"}


def unique_user() -> str:
    return f"u{uuid.uuid4().hex[:10]}"


def make_headers() -> dict:
    return auth_headers(unique_user())


# =========================================================
# AUTHENTICATION TESTS
# =========================================================

class TestAuthentication:

    def test_register_success(self):
        """New user can register successfully."""
        res = client.post("/api/auth/register", json={
            "username": unique_user(),
            "password": "password123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "user_id" in data
        assert data["message"] == "User registered successfully"

    def test_register_duplicate_username(self):
        """Registering with an existing username returns 400."""
        name = unique_user()
        client.post("/api/auth/register", json={"username": name, "password": "pass123"})
        res = client.post("/api/auth/register", json={"username": name, "password": "pass123"})
        assert res.status_code == 400
        assert "already exists" in res.json()["detail"].lower()

    def test_register_missing_fields(self):
        """Registration without required fields returns 422."""
        res = client.post("/api/auth/register", json={"username": "incomplete"})
        assert res.status_code == 422

    def test_login_success(self):
        """Registered user can login and receive JWT token."""
        name = unique_user()
        client.post("/api/auth/register", json={"username": name, "password": "securepass"})
        res = client.post("/api/auth/login", json={"username": name, "password": "securepass"})
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data

    def test_login_wrong_password(self):
        """Login with wrong password returns 401."""
        name = unique_user()
        client.post("/api/auth/register", json={"username": name, "password": "correct"})
        res = client.post("/api/auth/login", json={"username": name, "password": "wrong"})
        assert res.status_code == 401

    def test_login_nonexistent_user(self):
        """Login with non-existent username returns 401."""
        res = client.post("/api/auth/login", json={"username": "ghost_" + uuid.uuid4().hex, "password": "pass"})
        assert res.status_code == 401

    def test_me_endpoint_authenticated(self):
        """Authenticated /me returns current user info."""
        name = unique_user()
        headers = auth_headers(name)
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["username"] == name

    def test_me_endpoint_unauthenticated(self):
        """Unauthenticated /me returns 403."""
        res = client.get("/api/auth/me")
        assert res.status_code in (401, 403)

    def test_protected_route_with_invalid_token(self):
        """Invalid JWT returns 401 or 403 on protected routes."""
        res = client.get("/api/projects", headers={"Authorization": "Bearer invalid.token.here"})
        assert res.status_code in (401, 403)

    def test_protected_route_without_token(self):
        """No token returns 401 or 403 on protected routes."""
        res = client.get("/api/projects")
        assert res.status_code in (401, 403)


# =========================================================
# PROJECT TESTS
# =========================================================

class TestProjects:

    def setup_method(self):
        self.headers = make_headers()

    def test_create_project_minimal(self):
        """User can create a project with just a name."""
        res = client.post("/api/projects", json={"project_name": "My Hack"}, headers=self.headers)
        assert res.status_code == 201
        data = res.json()
        assert data["project_name"] == "My Hack"
        assert data["current_stage"] == "problem_discovery"
        assert data["progress"] == 0

    def test_create_project_full(self):
        """User can create a project with all fields."""
        payload = {
            "project_name": "Full Project",
            "hackathon_name": "IBM Hack 2025",
            "theme": "Education",
            "interests": "AI, ML",
            "skills": "Python, React",
            "team_info": "3 members",
            "constraints": "24 hours",
        }
        res = client.post("/api/projects", json=payload, headers=self.headers)
        assert res.status_code == 201
        data = res.json()
        assert data["hackathon_name"] == "IBM Hack 2025"
        assert data["theme"] == "Education"

    def test_create_project_missing_name(self):
        """Creating a project without a name returns 422."""
        res = client.post("/api/projects", json={"hackathon_name": "X"}, headers=self.headers)
        assert res.status_code == 422

    def test_list_projects(self):
        """User can list their projects."""
        client.post("/api/projects", json={"project_name": "P1"}, headers=self.headers)
        client.post("/api/projects", json={"project_name": "P2"}, headers=self.headers)
        res = client.get("/api/projects", headers=self.headers)
        assert res.status_code == 200
        names = [p["project_name"] for p in res.json()]
        assert "P1" in names
        assert "P2" in names

    def test_get_project(self):
        """User can retrieve a specific project."""
        create_res = client.post("/api/projects", json={"project_name": "GetMe"}, headers=self.headers)
        pid = create_res.json()["id"]
        res = client.get(f"/api/projects/{pid}", headers=self.headers)
        assert res.status_code == 200
        assert res.json()["project_name"] == "GetMe"
        assert "stages" in res.json()

    def test_get_nonexistent_project(self):
        """Fetching a project that doesn't exist returns 404."""
        res = client.get("/api/projects/999999", headers=self.headers)
        assert res.status_code == 404

    def test_update_project(self):
        """User can update project fields."""
        create_res = client.post("/api/projects", json={"project_name": "OldName"}, headers=self.headers)
        pid = create_res.json()["id"]
        res = client.patch(f"/api/projects/{pid}", json={"project_name": "NewName"}, headers=self.headers)
        assert res.status_code == 200
        assert res.json()["project_name"] == "NewName"

    def test_delete_project(self):
        """User can delete their own project."""
        create_res = client.post("/api/projects", json={"project_name": "ToDelete"}, headers=self.headers)
        pid = create_res.json()["id"]
        del_res = client.delete(f"/api/projects/{pid}", headers=self.headers)
        assert del_res.status_code == 204
        get_res = client.get(f"/api/projects/{pid}", headers=self.headers)
        assert get_res.status_code == 404

    def test_cannot_access_another_users_project(self):
        """User A cannot access User B's project."""
        headers_a = make_headers()
        create_res = client.post("/api/projects", json={"project_name": "User A Project"}, headers=headers_a)
        pid = create_res.json()["id"]
        headers_b = make_headers()
        res = client.get(f"/api/projects/{pid}", headers=headers_b)
        assert res.status_code == 404

    def test_cannot_delete_another_users_project(self):
        """User A cannot delete User B's project."""
        headers_a = make_headers()
        create_res = client.post("/api/projects", json={"project_name": "Protected"}, headers=headers_a)
        pid = create_res.json()["id"]
        headers_b = make_headers()
        res = client.delete(f"/api/projects/{pid}", headers=headers_b)
        assert res.status_code == 404

    def test_project_has_all_ten_stages(self):
        """Project response includes all 10 stages."""
        create_res = client.post("/api/projects", json={"project_name": "AllStages"}, headers=self.headers)
        pid = create_res.json()["id"]
        res = client.get(f"/api/projects/{pid}", headers=self.headers)
        stage_keys = [s["stage"] for s in res.json()["stages"]]
        for key in ["problem_discovery", "problem_validation", "solution_ideation",
                    "product_planning", "technical_architecture", "development",
                    "testing", "responsible_ai", "documentation", "pitch_submission"]:
            assert key in stage_keys


# =========================================================
# STAGE TESTS
# =========================================================

class TestStages:

    def setup_method(self):
        self.headers = make_headers()
        create_res = client.post("/api/projects", json={
            "project_name": "Stage Test Project",
            "theme": "Education",
            "interests": "AI",
            "skills": "Python",
        }, headers=self.headers)
        assert create_res.status_code == 201
        self.pid = create_res.json()["id"]

    def test_get_stage_pending(self):
        """Getting a stage that hasn't started returns pending status."""
        res = client.get(f"/api/projects/{self.pid}/stages/problem_discovery", headers=self.headers)
        assert res.status_code == 200
        data = res.json()
        assert data["stage"] == "problem_discovery"
        assert data["status"] == "pending"
        assert data["chat_history"] == []

    def test_get_invalid_stage(self):
        """Getting an invalid stage name returns 400."""
        res = client.get(f"/api/projects/{self.pid}/stages/not_a_real_stage", headers=self.headers)
        assert res.status_code == 400

    def test_complete_stage_advances(self):
        """Completing a stage updates status and advances project stage."""
        res = client.post(f"/api/projects/{self.pid}/stages/problem_discovery/complete",
                          json={"advance": True}, headers=self.headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["next_stage"] == "problem_validation"

    def test_complete_stage_no_advance(self):
        """Completing a stage with advance=False doesn't advance."""
        headers = make_headers()
        p = client.post("/api/projects", json={"project_name": "NoAdv"}, headers=headers).json()
        res = client.post(f"/api/projects/{p['id']}/stages/problem_discovery/complete",
                          json={"advance": False}, headers=headers)
        assert res.status_code == 200
        assert res.json()["next_stage"] is None

    def test_progress_updates_on_complete(self):
        """Progress increases when stages are completed."""
        client.post(f"/api/projects/{self.pid}/stages/problem_discovery/complete",
                    json={"advance": True}, headers=self.headers)
        project = client.get(f"/api/projects/{self.pid}", headers=self.headers).json()
        assert project["progress"] > 0

    def test_update_invalid_stage_returns_400(self):
        """Updating project to invalid stage returns 400."""
        res = client.patch(f"/api/projects/{self.pid}",
                           json={"current_stage": "not_real"}, headers=self.headers)
        assert res.status_code == 400

    def test_complete_last_stage(self):
        """Completing the last stage returns None for next_stage."""
        headers = make_headers()
        p = client.post("/api/projects", json={"project_name": "LastStage"}, headers=headers).json()
        res = client.post(f"/api/projects/{p['id']}/stages/pitch_submission/complete",
                          json={"advance": True}, headers=headers)
        assert res.status_code == 200
        assert res.json()["next_stage"] is None


# =========================================================
# ORCHESTRATOR / AGENT TESTS
# =========================================================

class TestOrchestrator:

    def test_stage_order_is_complete(self):
        """STAGE_ORDER contains all 10 expected stages."""
        from app.agent_core.hackathon_agents import STAGE_ORDER
        assert len(STAGE_ORDER) == 10
        assert STAGE_ORDER[0] == "problem_discovery"
        assert STAGE_ORDER[-1] == "pitch_submission"

    def test_agent_map_has_all_stages(self):
        """AGENT_MAP has an agent function for each stage."""
        from app.agent_core.hackathon_agents import AGENT_MAP, STAGE_ORDER
        for stage in STAGE_ORDER:
            assert stage in AGENT_MAP, f"Missing agent for stage: {stage}"
            assert callable(AGENT_MAP[stage])

    def test_stage_labels_complete(self):
        """STAGE_LABELS has a label for each stage."""
        from app.agent_core.hackathon_agents import STAGE_LABELS, STAGE_ORDER
        for stage in STAGE_ORDER:
            assert stage in STAGE_LABELS

    def test_calculate_progress_empty(self):
        """Progress is 0 when no stages are completed."""
        from app.agent_core.hackathon_orchestrator import calculate_progress
        assert calculate_progress([]) == 0

    def test_calculate_progress_all_complete(self):
        """Progress is 100 when all 10 stages completed."""
        from app.agent_core.hackathon_orchestrator import calculate_progress

        class FakeStage:
            def __init__(self):
                self.status = "completed"

        stages = [FakeStage() for _ in range(10)]
        assert calculate_progress(stages) == 100

    def test_calculate_progress_partial(self):
        """Progress is proportional to completed stages."""
        from app.agent_core.hackathon_orchestrator import calculate_progress

        class FakeStage:
            def __init__(self, status):
                self.status = status

        stages = [FakeStage("completed")] * 5 + [FakeStage("pending")] * 5
        result = calculate_progress(stages)
        assert result == 50

    def test_get_next_stage(self):
        """get_next_stage returns the correct next stage."""
        from app.agent_core.hackathon_orchestrator import get_next_stage
        assert get_next_stage("problem_discovery") == "problem_validation"
        assert get_next_stage("solution_ideation") == "product_planning"

    def test_get_next_stage_last(self):
        """get_next_stage returns None for the last stage."""
        from app.agent_core.hackathon_orchestrator import get_next_stage
        assert get_next_stage("pitch_submission") is None

    def test_get_next_stage_invalid(self):
        """get_next_stage returns None for invalid stage."""
        from app.agent_core.hackathon_orchestrator import get_next_stage
        assert get_next_stage("not_real") is None

    def test_build_project_context(self):
        """build_project_context creates a correct context dict."""
        from app.agent_core.hackathon_orchestrator import build_project_context

        class FakeProject:
            project_name = "Test"
            hackathon_name = "HackX"
            theme = "AI"
            interests = "ML"
            skills = "Python"
            team_info = "2 members"
            constraints = "24 hours"
            current_stage = "problem_discovery"

        ctx = build_project_context(FakeProject(), [])
        assert ctx["project_name"] == "Test"
        assert ctx["hackathon_name"] == "HackX"
        assert ctx["stage_outputs"] == {}

    def test_route_to_agent_returns_string(self):
        """route_to_agent calls the correct agent and returns a string (mocked)."""
        from app.agent_core import hackathon_orchestrator as orch
        from app.agent_core import hackathon_agents as agents

        def fake_agent(msg, ctx, hist):
            return "Problem discovery response"

        original = agents.AGENT_MAP["problem_discovery"]
        agents.AGENT_MAP["problem_discovery"] = fake_agent
        try:
            result = orch.route_to_agent(
                stage="problem_discovery",
                user_message="help me",
                project_ctx={},
                chat_history=[],
            )
            assert result == "Problem discovery response"
        finally:
            agents.AGENT_MAP["problem_discovery"] = original


# =========================================================
# HEALTH CHECK
# =========================================================

class TestHealth:

    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["status"] == "online"

    def test_health(self):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"
