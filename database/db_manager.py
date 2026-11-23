
import sqlite3
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "interviewiq.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            session_date TEXT NOT NULL,
            total_questions INTEGER NOT NULL,
            average_correctness REAL,
            average_clarity REAL,
            average_depth REAL,
            overall_score REAL,
            report TEXT NOT NULL,
            evaluations TEXT NOT NULL,
            answers TEXT DEFAULT '[]',
            followups TEXT DEFAULT '[]'
        )
    """)

    cursor.execute("PRAGMA table_info(interview_sessions)")
    existing_columns = {
        column[1] for column in cursor.fetchall()
    }

    if "answers" not in existing_columns:
        cursor.execute("""
            ALTER TABLE interview_sessions
            ADD COLUMN answers TEXT DEFAULT '[]'
        """)

    if "followups" not in existing_columns:
        cursor.execute("""
            ALTER TABLE interview_sessions
            ADD COLUMN followups TEXT DEFAULT '[]'
        """)

    connection.commit()
    connection.close()


def save_interview_session(
    role,
    evaluations,
    report,
    answers=None,
    followups=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interview_sessions (
            role,
            session_date,
            total_questions,
            average_correctness,
            average_clarity,
            average_depth,
            overall_score,
            report,
            evaluations,
            answers,
            followups
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        role,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        report.total_questions,
        report.average_correctness,
        report.average_clarity,
        report.average_depth,
        report.overall_score,
        report.model_dump_json(),
        json.dumps(evaluations),
        json.dumps(answers or []),
        json.dumps(followups or [])
    ))

    connection.commit()

    session_id = cursor.lastrowid

    connection.close()

    return session_id


def get_all_sessions():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            role,
            session_date,
            total_questions,
            average_correctness,
            average_clarity,
            average_depth,
            overall_score
        FROM interview_sessions
        ORDER BY id DESC
    """)

    sessions = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return sessions


def get_session_details(session_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM interview_sessions WHERE id = ?",
        (session_id,)
    )

    session = cursor.fetchone()

    connection.close()

    if session is None:
        return None

    session = dict(session)

    session["report"] = json.loads(session["report"])
    session["evaluations"] = json.loads(session["evaluations"])
    session["answers"] = json.loads(session["answers"] or "[]")
    session["followups"] = json.loads(session["followups"] or "[]")

    return session
