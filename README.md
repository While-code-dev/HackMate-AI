# HackMate AI 🚀

> **An AI-powered hackathon copilot that guides teams from idea to submission.**

HackMate AI is a multi-agent system that walks you through every stage of the hackathon journey — from problem discovery to pitch delivery — using specialized AI agents at each step.

---

## Problem Statement

Students entering hackathons struggle to:
- Identify meaningful, well-scoped problems
- Validate their ideas before investing hours of development
- Plan realistic MVPs within 24–48 hours
- Structure their technical architecture efficiently
- Prepare compelling pitches under time pressure

No single tool guides teams through the **complete** hackathon journey.

---

## Solution

HackMate AI provides a **structured, AI-assisted journey** where 10 specialized agents collaborate to guide your team from the first idea to the final submission — each knowing everything the previous agents discovered.

---

## Core Features

- 🎯 **10-Stage Hackathon Journey** — Problem Discovery → Pitch & Submission
- 🤖 **10 Specialized AI Agents** — Each expert in their stage
- 🧠 **Shared Project Context** — Agents know what previous agents discovered
- 💬 **Chat Interface per Stage** — Natural conversation with each agent
- 📊 **Progress Tracking** — Visual pipeline and percentage progress
- 🔐 **Secure Authentication** — JWT-based login with hashed passwords
- 💾 **Full Persistence** — Resume projects after closing the browser
- 🛡️ **Responsible AI** — AI-generated badge, disclaimers, human oversight
- 🧪 **Automated Test Suite** — 41 tests covering all critical paths

---

## Multi-Agent Architecture

```
User Input
    ↓
Central Orchestrator (routes by stage)
    ↓
┌─────────────────────────────────────────────────────┐
│  Agent 1: Problem Discovery                          │
│  Agent 2: Problem Validation                         │
│  Agent 3: Solution Ideation                          │
│  Agent 4: Product Planning                           │
│  Agent 5: Technical Architecture                     │
│  Agent 6: Development Assistance                     │
│  Agent 7: Testing & QA                               │
│  Agent 8: Responsible AI & Security                  │
│  Agent 9: Documentation                              │
│  Agent 10: Pitch & Submission                        │
└─────────────────────────────────────────────────────┘
    ↓
Responses stored with full project context
```

### Agent Responsibilities

| Agent | Stage | What It Does |
|-------|-------|-------------|
| Problem Discovery | Stage 1 | Surfaces real-world problems from your interests/theme |
| Problem Validation | Stage 2 | Validates feasibility, target users, risks |
| Solution Ideation | Stage 3 | Generates and compares 3-4 solution approaches |
| Product Planning | Stage 4 | Defines MVP, user stories, must-have features |
| Technical Architecture | Stage 5 | Recommends stack, architecture, implementation plan |
| Development | Stage 6 | Coding guidance, debugging, starter code |
| Testing & QA | Stage 7 | Test checklists, edge cases, demo readiness |
| Responsible AI & Security | Stage 8 | Privacy, security, AI ethics review |
| Documentation | Stage 9 | README, architecture docs, setup instructions |
| Pitch & Submission | Stage 10 | Elevator pitch, demo flow, submission checklist |

### How Context Flows

Every agent receives the full project context: hackathon name, theme, interests, skills, team info, and all previous agents' outputs. This means:
- The Technical Architecture agent knows the validated problem AND chosen solution
- The Development agent knows the architecture that was designed
- The Pitch agent knows the full project story end-to-end

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  React Frontend (Vite)               │
│  - Login/Register                                    │
│  - Project Dashboard                                 │
│  - Stage Workspaces (chat with each agent)           │
│  - Progress visualization                            │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST (/api/*)
┌────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                     │
│  - /api/auth/* — JWT authentication                 │
│  - /api/projects/* — Project CRUD                   │
│  - /api/projects/{id}/stages/* — Stage interactions  │
│  - /api/chat — Legacy chat endpoint                  │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐        ┌─────────────────────┐
│  SQLite DB   │        │  Google Gemini API  │
│ hackmate.db  │        │  gemini-2.0-flash   │
└──────────────┘        └─────────────────────┘
```

---

## Technology Stack

**Frontend**
- React 19
- Vite 8
- Axios (API client with JWT interceptor)
- Lucide React (icons)

**Backend**
- Python 3.13
- FastAPI
- SQLAlchemy 2.0 + SQLite
- LangChain + `langchain-google-genai`
- Google Gemini (`gemini-2.0-flash`)
- PyJWT (JWT authentication)
- pwdlib (Argon2 password hashing)
- Pydantic v2

**Testing**
- pytest
- FastAPI TestClient (httpx)

---

## Project Structure

```
HackMate-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, startup, DB init
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   ├── models.py                  # User, Conversation, HackathonProject, StageData
│   │   ├── auth.py                    # JWT creation/verification, password hashing
│   │   ├── auth_routes.py             # /api/auth/* endpoints
│   │   ├── api/
│   │   │   ├── projects.py            # /api/projects/* CRUD
│   │   │   ├── stages.py              # /api/projects/{id}/stages/* chat & complete
│   │   │   ├── chat.py                # /api/chat (legacy endpoint)
│   │   │   └── bob.py                 # /api/bob/scaffold (IBM Bob integration)
│   │   ├── agent_core/
│   │   │   ├── hackathon_agents.py    # 10 specialized agent functions
│   │   │   ├── hackathon_orchestrator.py  # Context builder, router, progress calc
│   │   │   ├── schemas.py             # Pydantic schemas for structured AI output
│   │   │   ├── orchestrator.py        # Legacy orchestrator (kept for /api/chat)
│   │   │   └── sub_agents.py          # Legacy sub-agents
│   │   └── services/
│   │       └── bob_runner.py          # IBM Bob CLI subprocess wrapper
│   ├── tests/
│   │   └── test_hackmate.py           # 41 automated tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # All pages and components
│   │   ├── api.js                     # Axios instance with JWT interceptor
│   │   └── index.css                  # Full design system
│   ├── vite.config.js                 # Vite + proxy to :8000
│   └── package.json
├── AGENTS.md
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Google Gemini API key (free tier works)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example app/.env
# Edit app/.env and fill in:
#   GEMINI_API_KEY=your_key_here
#   JWT_SECRET_KEY=your_random_secret_here
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the Application

### Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at: http://127.0.0.1:8000

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: http://localhost:5173

The Vite dev server proxies all `/api/*` requests to the backend automatically.

---

## Environment Variables

The `.env` file must be placed at `backend/app/.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key
JWT_SECRET_KEY=your_random_jwt_secret_at_least_32_chars

# IBM Bob integration (optional)
BOB_EXECUTABLE_PATH=bob
BOB_API_KEY=
BOB_TIMEOUT_SECONDS=120
```

> **Note:** The `.env.example` at `backend/` root documents `JWT_SECRET` but the code reads `JWT_SECRET_KEY`. Always use `JWT_SECRET_KEY`.

---

## Testing

Run from the `backend/` directory:

```bash
cd backend
pytest tests/test_hackmate.py -v
```

Test coverage:
- **Authentication**: register, login, duplicate users, invalid tokens, protected routes, `/me` endpoint
- **Projects**: create, list, get, update, delete, cross-user security
- **Stages**: get pending, complete, advance, progress calculation, invalid stages
- **Orchestrator**: agent routing, context building, progress calculation, next stage logic
- **Health checks**: `/` and `/health`

**41 tests, 0 failures**

---

## API Endpoints

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET  | `/api/auth/me` | Get current user (requires JWT) |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/projects` | Create a new hackathon project |
| GET | `/api/projects` | List user's projects |
| GET | `/api/projects/{id}` | Get project with all stage data |
| PATCH | `/api/projects/{id}` | Update project metadata |
| DELETE | `/api/projects/{id}` | Delete project |

### Stages
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/projects/{id}/stages/{stage}/chat` | Send message to stage agent |
| GET | `/api/projects/{id}/stages/{stage}` | Get stage history + AI outputs |
| POST | `/api/projects/{id}/stages/{stage}/complete` | Mark stage done, optionally advance |

---

## Responsible AI

HackMate AI follows responsible AI practices:

1. **AI-generated content labeling** — Every AI response is marked with an "AI-generated" badge
2. **Human-in-the-loop** — Users confirm stage completion; AI never auto-advances
3. **Verification disclaimer** — Every chat includes: *"Review and verify before relying on them for important decisions"*
4. **No sensitive data collection** — Only username and project details are stored
5. **Transparent AI usage** — The Responsible AI & Security stage explicitly reviews the user's own project for AI risks
6. **Hallucination awareness** — Agents acknowledge uncertainty and encourage validation

---

## Security Considerations

- Passwords are hashed using Argon2 (via `pwdlib[argon2]`) — never stored as plaintext
- JWT tokens expire after 60 minutes
- All project endpoints verify ownership — users cannot access each other's data
- API keys are stored in environment variables, never in code or frontend
- CORS is restricted to `localhost:5173` and `127.0.0.1:5173` in development
- Input validation via Pydantic on all API endpoints

---

## Future Improvements

- Email-based authentication and password reset
- Real-time collaboration (multiple team members per project)
- Export project to PDF/Markdown
- Integration with GitHub for code scaffolding
- Hackathon event calendar and deadline tracking
- Mobile-responsive PWA
- Team chat and task assignment within projects

---

## License

MIT License — free for personal, educational, and commercial use.
