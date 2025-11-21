from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "neurolearn.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                raw_text TEXT,
                simplified_text TEXT,
                level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_session(user_id: str, raw_text: str, simplified_text: str, level: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (user_id, raw_text, simplified_text, level)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, raw_text, simplified_text, level),
        )
        conn.commit()


def save_quiz_result(user_id: str, score: float) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quizzes (user_id, score)
            VALUES (?, ?)
            """,
            (user_id, score),
        )
        conn.commit()


def get_progress(user_id: str) -> Dict[str, Any]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT level, created_at FROM sessions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,),
        )
        sessions = cursor.fetchall()

        cursor.execute(
            """
            SELECT score, created_at FROM quizzes
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (user_id,),
        )
        quizzes = cursor.fetchall()

    return {
        "sessions": [
            {"level": level, "timestamp": timestamp} for level, timestamp in sessions
        ],
        "quizzes": [
            {"score": score, "timestamp": timestamp} for score, timestamp in quizzes
        ],
    }

