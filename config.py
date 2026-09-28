"""
config.py
==========
Central configuration for the CareerAI application.

Keeping all tunables in one place makes the project easier to explain
during a viva/demo: a faculty member can be shown exactly where the
scoring weights, file paths, and model names live.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "database" / "careerai.db"
SAMPLE_JD_DIR = DATA_DIR / "sample_job_descriptions"
SKILLS_CSV = DATA_DIR / "skills.csv"
QUESTION_BANK_JSON = DATA_DIR / "interview_questions.json"

# Uploaded resumes are processed in-memory / in a temp folder and are NOT
# permanently retained, in line with the privacy statement made on the
# About page.
TEMP_UPLOAD_DIR = BASE_DIR / "temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_PATH.parent, exist_ok=True)

# ---------------------------------------------------------------------------
# NLP / semantic similarity engine configuration
# ---------------------------------------------------------------------------
# Primary engine: sentence-transformers (local, free, no API key).
# Fallback engine: TF-IDF + cosine similarity (pure scikit-learn, always
# available) used automatically if the transformer model cannot be loaded
# (e.g. no internet on first run to fetch model weights).
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL = "en_core_web_sm"

# ---------------------------------------------------------------------------
# Job-matching score weights
# ---------------------------------------------------------------------------
# Final Match Score = SEMANTIC_WEIGHT * semantic_similarity
#                    + SKILL_OVERLAP_WEIGHT * skill_overlap_score
# This is an academic scoring heuristic, NOT a validated recruitment metric.
SEMANTIC_WEIGHT = 0.6
SKILL_OVERLAP_WEIGHT = 0.4

# Skill match thresholds (cosine similarity between resume-skill embedding
# and JD-skill embedding) used to classify a JD skill as Strong / Partial /
# Missing when it is not found as an exact/alias string match.
STRONG_MATCH_THRESHOLD = 0.80
PARTIAL_MATCH_THRESHOLD = 0.55

# ---------------------------------------------------------------------------
# Interview configuration
# ---------------------------------------------------------------------------
QUESTION_COUNT_OPTIONS = [5, 10, 15]
DIFFICULTY_OPTIONS = ["Easy", "Medium", "Hard", "Mixed"]
QUESTION_TYPE_OPTIONS = ["Technical", "HR", "Mixed"]

# Answer evaluation weights (all out of 10, combined into an overall /10)
ANSWER_WEIGHTS = {
    "relevance": 0.35,
    "concept_coverage": 0.35,
    "completeness": 0.30,
}

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
APP_TITLE = "CareerAI — AI-Powered Career Intelligence & Mock Interview System"
APP_ICON = "🧭"
RANDOM_SEED = 42
