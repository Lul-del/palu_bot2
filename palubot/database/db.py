import os
import sqlite3
from pathlib import Path
from typing import Iterable

# Sur Render, on utilise /tmp qui est accessible en écriture.
# En local, on garde le dossier du projet.
_DEFAULT_DB = Path(__file__).resolve().parent / "users.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_DEFAULT_DB)))


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS triage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                risk TEXT,
                answers TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reminder_time TEXT,
                text TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def upsert_user(user_id: int, first_name: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, first_name)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET first_name=excluded.first_name
            """,
            (user_id, first_name),
        )


def save_triage(user_id: int, score: int, risk: str, answers: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO triage_history (user_id, score, risk, answers) VALUES (?, ?, ?, ?)",
            (user_id, score, risk, answers),
        )


def add_reminder(user_id: int, reminder_time: str, text: str) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO reminders (user_id, reminder_time, text) VALUES (?, ?, ?)",
            (user_id, reminder_time, text),
        )
        return int(cur.lastrowid)


def list_active_reminders(user_id: int) -> Iterable[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, reminder_time, text FROM reminders WHERE user_id=? AND active=1 ORDER BY id DESC",
            (user_id,),
        ).fetchall()
