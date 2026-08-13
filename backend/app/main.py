from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.bob import router as bob_router
from app.auth_routes import router as auth_router
from app.database import engine, Base
from app import models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HackMate AI API",
    description="Backend API for the HackMate AI multi-agent hackathon assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(bob_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "HackMate AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }