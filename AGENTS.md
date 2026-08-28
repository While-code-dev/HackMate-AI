# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview
HackMate AI — a multi-agent AI hackathon copilot. **FastAPI** backend (Python 3.13) + **React 19 + Vite** frontend. SQLite database. Google Gemini via LangChain.

## Commands

### Backend (run from `backend/`)
```
uvicorn app.main:app --reload        # Start dev server (port 8000)
pytest tests/test_hackmate.py -v     # Run 41 tests
python gemini_test.py                # Test Gemini API connectivity
```

### Frontend (run from `frontend/`)
```
npm run dev      # Dev server on :5173, proxies /api → :8000
npm run build    # Production build
npm run lint     # ESLint
```

## Required Environment: `backend/app/.env`
```
GEMINI_API_KEY=          # also checks GOOGLE_API_KEY as fallback
JWT_SECRET_KEY=          # Note: NOT JWT_SECRET — .env.example has the wrong name
BOB_EXECUTABLE_PATH=bob
BOB_API_KEY=
BOB_TIMEOUT_SECONDS=120
```

## Critical Architecture Notes

- **DB tables created on startup** — `main.py` calls `Base.metadata.create_all(bind=engine)` at startup (safe no-op if already exist). `hackmate.db` lives in `backend/` (where uvicorn runs).
- **LLM instantiated fresh per agent call** — `_llm()` is called inside each of the 10 agent functions. Do not refactor to share an instance.
- **Project context flows across agents** — `build_project_context()` in `hackathon_orchestrator.py` collects all previous stage outputs and passes them to every agent call.
- **Bob scaffold endpoint never raises on Bob failures** — always returns `status="error"` in `BobScaffoldResponse`.
- **`project_spec` on Conversation** is stored as `json.dumps(dict)` in a Text column — not a JSON column.
- **JWT env var**: code reads `JWT_SECRET_KEY`; `.env.example` incorrectly documents `JWT_SECRET`.
- **Frontend uses `api.js`** (shared Axios instance) for all calls — has JWT auto-injection. Never add `fetch()` calls directly.
- **All frontend "pages" live in `src/App.jsx`** — no file-based routing. Navigation is state-driven (`view` variable in `AppShell`).

## Code Style (Backend)
- Each SQLAlchemy `Column(...)` argument on its own line.
- Pydantic `BaseModel` for all request/response schemas.
- Structured LLM output via `llm.with_structured_output(PydanticModel)` in legacy agents.
- New hackathon agents use plain `_llm().invoke(prompt).content` (string output).
- `datetime.utcnow()` is used (deprecated but functional — don't change without testing).

## Code Style (Frontend)
- Plain `.jsx` / `.js` — no TypeScript.
- All API calls use `api` from `./api.js`.
- Token stored as `"token"` key in localStorage.
- CSS classes in `index.css` — no CSS modules or styled components.

## Testing
- Tests use `pytest` + `FastAPI TestClient` (httpx).
- Test file patches `app.database.engine` before importing `app.main` to route all DB ops to a test SQLite file.
- Test DB file: `backend/test_hackmate.db` (cleaned up after test run).
- Run from `backend/` directory, not `backend/tests/`.
