# Project Coding Rules (Non-Obvious Only)

- **Never call `Base.metadata.create_all()` manually** — it's called automatically in `main.py` at startup. Adding new models just requires them to be imported before that line runs.
- **`project_spec` on Conversation is `json.dumps(dict)` in a Text column** — always `json.dumps()` before writing, `json.loads()` after reading.
- **JWT env var mismatch**: `.env.example` says `JWT_SECRET` but code reads `JWT_SECRET_KEY` — always use `JWT_SECRET_KEY`.
- **All 10 stage agents create a fresh `_llm()` instance** — this is intentional. Do not refactor to share an LLM instance across agents.
- **`route_to_agent()` in `hackathon_orchestrator.py` is the single dispatch point** — add new stage agents by adding an entry to `AGENT_MAP` in `hackathon_agents.py` and a corresponding entry in `STAGE_ORDER` and `STAGE_LABELS`.
- **Stage chat endpoint (`stages.py`) never raises on AI failure** — always catches exceptions and returns an error message as the AI response.
- **Bob scaffold endpoint never raises HTTP exceptions on Bob runtime errors** — return `BobScaffoldResponse` with `status="error"`.
- **All frontend API calls must use the Axios instance from `src/api.js`** — it handles JWT injection. No `fetch()` calls.
- **All frontend "pages" are functions in `src/App.jsx`** — add new pages there and add a branch in `AppShell.renderContent()`.
- **Progress calculation**: only `status === "completed"` stages count; `in_progress` does not add to progress.
