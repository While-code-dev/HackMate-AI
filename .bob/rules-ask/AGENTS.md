# Project Documentation Context (Non-Obvious Only)

- **`backend/app/.env`** is where the env file must live — all modules resolve it as `Path(__file__).parent.parent / ".env"` relative to their own file location.
- **`.env.example` at `backend/` root has a wrong key name**: documents `JWT_SECRET` but code reads `JWT_SECRET_KEY`.
- **No test framework was configured initially** — `test_agent.py` and `gemini_test.py` are standalone scripts, not pytest suites. The proper pytest suite is at `backend/tests/test_hackmate.py`.
- **`frontend/src/App.jsx` is a single-file app** (~600+ lines). All page components, routing logic, API calls, and styles co-exist in one file.
- **The Bob scaffold feature** (`/api/bob/scaffold`) invokes the IBM Bob CLI binary as a subprocess (`bob run --format json <prompt>`), not a Langchain agent or API call.
- **`react-router-dom` is installed but unused** — navigation is controlled by the `view` state variable in `AppShell`.
- **The `/api/chat` endpoint** (legacy) still works but is NOT used by the new project workspace UI. Stage chat uses `/api/projects/{id}/stages/{stage}/chat` instead.
- **`lucide-react@1.33.0`** is used for icons — icon names follow PascalCase (e.g., `FlaskConical`, not `BeakerIcon`).
