from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables at startup
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

from app.database import engine, Base
from app.auth_routes import router as auth_router
from app.api.chat import router as chat_router
from app.api.bob import router as bob_router
from app.api.projects import router as projects_router
from app.api.stages import router as stages_router


# Create all tables on startup (safe no-op if tables already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HackMate AI",
    description="Multi-agent AI hackathon copilot",
    version="2.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

   allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://hackmate-ai-1.onrender.com",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(bob_router)
app.include_router(projects_router)
app.include_router(stages_router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():
    return {
        "message": "HackMate AI backend is running",
        "status": "online",
        "version": "2.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
