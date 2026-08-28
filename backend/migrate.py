"""Run once to add new tables to the existing hackmate.db."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "hackmate.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS hackathon_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    project_name TEXT NOT NULL,
    hackathon_name TEXT,
    theme TEXT,
    interests TEXT,
    skills TEXT,
    team_info TEXT,
    constraints TEXT,
    current_stage TEXT NOT NULL DEFAULT 'problem_discovery',
    progress INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stage_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES hackathon_projects(id),
    stage TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    user_inputs TEXT,
    ai_outputs TEXT,
    chat_history TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("Migration complete — hackathon_projects and stage_data tables created.")
