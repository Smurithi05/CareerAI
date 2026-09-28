"""
database/schema.py
=====================
SQLite schema (DDL) for the CareerAI application, kept separate from
database.py (connection/CRUD logic) and separate from the UI layer, as
required by the project specification.

All "blob-like" structured data (lists/dicts) is stored as JSON TEXT,
which is a common, simple approach for a student project using plain
SQLite (no need for a full ORM/ODM).
"""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS resume_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        candidate_name TEXT,
        skills_json TEXT,
        education_json TEXT,
        projects_json TEXT,
        internships_json TEXT,
        certifications_json TEXT,
        word_count INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS job_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        required_skills_json TEXT,
        preferred_skills_json TEXT,
        experience_json TEXT,
        education_requirements_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS skill_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        resume_analysis_id INTEGER,
        job_analysis_id INTEGER,
        semantic_similarity REAL,
        skill_overlap_score REAL,
        final_match_score REAL,
        matched_skills_json TEXT,
        missing_skills_json TEXT,
        partial_skills_json TEXT,
        engine_name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_role TEXT,
        num_questions INTEGER,
        difficulty TEXT,
        question_type TEXT,
        overall_score REAL,
        category_scores_json TEXT,
        weak_concepts_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS interview_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        question TEXT,
        category TEXT,
        difficulty TEXT,
        answer_text TEXT,
        relevance_score REAL,
        concept_coverage_score REAL,
        completeness_score REAL,
        overall_score REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES interview_sessions(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS career_roadmap (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prioritized_skills_json TEXT,
        weekly_plan_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """,
]
