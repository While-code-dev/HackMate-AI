from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    projects = relationship(
        "HackathonProject",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    project_spec = Column(
        Text,
        nullable=True,
        default=None
    )

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        Text,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


# =========================================================
# Hackathon Project
# =========================================================

class HackathonProject(Base):
    __tablename__ = "hackathon_projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    project_name = Column(
        Text,
        nullable=False
    )

    hackathon_name = Column(
        Text,
        nullable=True
    )

    theme = Column(
        Text,
        nullable=True
    )

    interests = Column(
        Text,
        nullable=True
    )

    skills = Column(
        Text,
        nullable=True
    )

    team_info = Column(
        Text,
        nullable=True
    )

    constraints = Column(
        Text,
        nullable=True
    )

    # Current stage: problem_discovery, problem_validation, solution_ideation,
    # product_planning, technical_architecture, development, testing,
    # responsible_ai, documentation, pitch_submission
    current_stage = Column(
        Text,
        nullable=False,
        default="problem_discovery"
    )

    # 0-100 percent complete
    progress = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="projects"
    )

    stages = relationship(
        "StageData",
        back_populates="project",
        cascade="all, delete-orphan"
    )


# =========================================================
# Stage Data
# =========================================================

class StageData(Base):
    __tablename__ = "stage_data"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("hackathon_projects.id"),
        nullable=False
    )

    stage = Column(
        Text,
        nullable=False
    )

    # pending | in_progress | completed
    status = Column(
        Text,
        nullable=False,
        default="pending"
    )

    # JSON-encoded user inputs for this stage
    user_inputs = Column(
        Text,
        nullable=True
    )

    # JSON-encoded AI outputs for this stage
    ai_outputs = Column(
        Text,
        nullable=True
    )

    # Chat history JSON for this stage
    chat_history = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    project = relationship(
        "HackathonProject",
        back_populates="stages"
    )
