"""
database/database.py
=======================
Thin SQLite persistence layer for CareerAI. Kept deliberately simple
(plain `sqlite3`, no ORM) so a final-year student can explain every query
in a viva. All UI code should call these functions rather than writing
raw SQL directly, to keep concerns separated as required by the spec.
"""

import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from config import DB_PATH
from database.schema import SCHEMA_STATEMENTS


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create all tables if they do not already exist. Safe to call every app start."""
    with get_connection() as conn:
        cur = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cur.execute(statement)


def _dumps(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except (TypeError, ValueError):
        return "[]"


def _loads(text: Optional[str]) -> Any:
    if not text:
        return []
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return []


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def get_or_create_user(name: str, email: Optional[str] = None) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE name = ? LIMIT 1", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Resume analysis
# ---------------------------------------------------------------------------
def save_resume_analysis(user_id: int, profile: Dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO resume_analysis
                (user_id, candidate_name, skills_json, education_json,
                 projects_json, internships_json, certifications_json, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                profile.get("name"),
                _dumps(profile.get("skills", [])),
                _dumps(profile.get("education", [])),
                _dumps(profile.get("projects", [])),
                _dumps(profile.get("internships", [])),
                _dumps(profile.get("certifications", [])),
                profile.get("word_count", 0),
            ),
        )
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Job analysis
# ---------------------------------------------------------------------------
def save_job_analysis(user_id: int, job_profile: Dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO job_analysis
                (user_id, role, required_skills_json, preferred_skills_json,
                 experience_json, education_requirements_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                job_profile.get("role"),
                _dumps(job_profile.get("required_skills", [])),
                _dumps(job_profile.get("preferred_skills", [])),
                _dumps(job_profile.get("experience", [])),
                _dumps(job_profile.get("education_requirements", [])),
            ),
        )
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Skill / job-match analysis
# ---------------------------------------------------------------------------
def save_skill_analysis(
    user_id: int,
    resume_analysis_id: int,
    job_analysis_id: int,
    match_result,
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO skill_analysis
                (user_id, resume_analysis_id, job_analysis_id, semantic_similarity,
                 skill_overlap_score, final_match_score, matched_skills_json,
                 missing_skills_json, partial_skills_json, engine_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                resume_analysis_id,
                job_analysis_id,
                match_result.semantic_similarity,
                match_result.skill_overlap_score,
                match_result.final_score,
                _dumps(match_result.matched_skills),
                _dumps(match_result.missing_skills),
                _dumps(match_result.partial_skills),
                match_result.engine_name,
            ),
        )
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Interview sessions & answers
# ---------------------------------------------------------------------------
def create_interview_session(
    user_id: int, job_role: str, num_questions: int, difficulty: str, question_type: str
) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO interview_sessions (user_id, job_role, num_questions, difficulty, question_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, job_role, num_questions, difficulty, question_type),
        )
        return cur.lastrowid


def update_interview_session_summary(session_id: int, summary) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE interview_sessions
            SET overall_score = ?, category_scores_json = ?, weak_concepts_json = ?
            WHERE id = ?
            """,
            (
                summary.overall_score,
                _dumps(summary.category_scores),
                _dumps(summary.weak_concepts),
                session_id,
            ),
        )


def save_interview_answer(session_id: int, question, evaluation) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO interview_answers
                (session_id, question, category, difficulty, answer_text,
                 relevance_score, concept_coverage_score, completeness_score, overall_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                question.question,
                question.category,
                question.difficulty,
                getattr(evaluation, "answer_text", ""),
                evaluation.relevance_score,
                evaluation.concept_coverage_score,
                evaluation.completeness_score,
                evaluation.overall_score,
            ),
        )
        return cur.lastrowid


def get_interview_sessions_for_user(user_id: int) -> List[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM interview_sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        )
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Roadmap
# ---------------------------------------------------------------------------
def save_roadmap(user_id: int, roadmap: Dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO career_roadmap (user_id, prioritized_skills_json, weekly_plan_json)
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                _dumps(roadmap.get("prioritized_skills", [])),
                _dumps(roadmap.get("weekly_plan", [])),
            ),
        )
        return cur.lastrowid


def get_latest_skill_analysis(user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM skill_analysis WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        )
        return cur.fetchone()
