# Project Architecture Constraints (Non-Obvious Only)

- **No migration system** — new SQLite columns must be `nullable=True` with no default. Adding NOT NULL columns to existing tables requires deleting `hackmate.db`.
- **Context sharing is done at request time** — `build_project_context()` reads all stage rows from the DB on every API call. There is no in-memory context cache.
- **10-stage sequential pipeline** — stages are ordered in `STAGE_ORDER` list. Progress advances strictly in order. Users can skip back to any stage but the "current_stage" only advances forward via the `/complete` endpoint.
- **`MasterOrchestrator` in `orchestrator.py` is a legacy singleton** — it serves the `/api/chat` endpoint only. The new multi-agent system uses `route_to_agent()` in `hackathon_orchestrator.py` which is stateless.
- **Frontend has no routing library** — all state (current view, active project ID, modal state) lives in `AppShell`. Any navigation change must update the `view` state.
- **Frontend axios timeout is 120 000 ms** to match `BOB_TIMEOUT_SECONDS=120`. If the AI timeout changes, both must be updated.
- **CORS allows only `localhost:5173` and `127.0.0.1:5173`** — any deployment or alternate port requires updating `main.py`.
- **Auth tokens expire in 60 minutes** (hardcoded in `auth.py`). There is no refresh token mechanism — users must re-login after expiry.
- **SQLite in-memory DB for tests** — tests patch `app.database.engine` before importing `app.main` to intercept the `create_all` call. This requires careful import ordering in test files.
- **AI model is `gemini-2.0-flash`** — hardcoded in `hackathon_agents.py` `_llm()` function. Change there to update the model globally.
