"""
utils/validators.py
======================
Centralized input validation so every page shows consistent,
user-friendly error messages instead of raw exceptions/stack traces.
"""

from typing import Optional

MIN_JD_WORDS = 15
MIN_ANSWER_CHARS = 1


def validate_job_description(text: str) -> Optional[str]:
    """Returns an error message if invalid, else None."""
    if not text or not text.strip():
        return "Please paste a job description before continuing."
    word_count = len(text.split())
    if word_count < MIN_JD_WORDS:
        return (
            f"The job description looks too short ({word_count} words). "
            f"Please provide at least {MIN_JD_WORDS} words for a meaningful analysis."
        )
    return None


def validate_resume_uploaded(uploaded_file) -> Optional[str]:
    if uploaded_file is None:
        return "Please upload a resume file (PDF or DOCX) to continue."
    return None


def validate_answer_text(text: str) -> Optional[str]:
    if text is None or len(text.strip()) < MIN_ANSWER_CHARS:
        return "Please type an answer (even a brief one) before submitting."
    return None


def validate_positive_int(value, field_name: str = "value") -> Optional[str]:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return f"{field_name} must be a whole number."
    if v <= 0:
        return f"{field_name} must be greater than zero."
    return None
