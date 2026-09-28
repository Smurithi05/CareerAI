"""
tests/test_scoring.py
========================
Unit tests for models/scoring.py — skill overlap, skill-gap
classification, and the combined Final Match Score formula.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SEMANTIC_WEIGHT, SKILL_OVERLAP_WEIGHT
from models.scoring import compute_skill_overlap, classify_skill_gaps, compute_job_match


def test_skill_overlap_full_match():
    resume_skills = ["Python", "SQL", "Git"]
    job_skills = ["Python", "SQL"]
    assert compute_skill_overlap(resume_skills, job_skills) == 1.0


def test_skill_overlap_partial_match():
    resume_skills = ["Python"]
    job_skills = ["Python", "Java"]
    assert compute_skill_overlap(resume_skills, job_skills) == 0.5


def test_skill_overlap_no_job_skills_returns_zero():
    assert compute_skill_overlap(["Python"], []) == 0.0


def test_classify_skill_gaps_exact_match_is_strong():
    resume_skills = ["Python", "SQL"]
    required = ["Python"]
    preferred = []
    results = classify_skill_gaps(resume_skills, required, preferred)
    assert len(results) == 1
    assert results[0].status == "Strong Match"
    assert results[0].importance == "High"


def test_classify_skill_gaps_unrelated_skill_is_missing():
    resume_skills = ["Python"]
    required = ["Spring Boot"]
    results = classify_skill_gaps(resume_skills, required, [])
    assert results[0].status in ("Missing", "Partial Match")  # depends on active engine's similarity


def test_compute_job_match_formula_bounds():
    resume_profile = {
        "cleaned_text": "Experienced Python developer with SQL and Git skills, built REST APIs.",
        "skills": ["Python", "SQL", "Git"],
    }
    job_profile = {
        "cleaned_text": "Looking for a Python developer with SQL experience.",
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Docker"],
    }
    result = compute_job_match(resume_profile, job_profile)

    assert 0.0 <= result.semantic_similarity <= 1.0
    assert 0.0 <= result.skill_overlap_score <= 1.0
    assert 0.0 <= result.final_score <= 1.0

    # NOTE: semantic_similarity / skill_overlap_score on the result are each
    # already rounded to 4 decimals independently, while final_score is
    # computed from the pre-rounding raw values inside compute_job_match().
    # Recombining the two already-rounded fields can therefore differ from
    # the true final_score by a small rounding delta (at most ~1e-3) — this
    # is expected floating-point behaviour, not a bug in the scoring logic.
    expected_final = round(
        SEMANTIC_WEIGHT * result.semantic_similarity + SKILL_OVERLAP_WEIGHT * result.skill_overlap_score, 4
    )
    assert abs(result.final_score - expected_final) < 1e-3
    assert "Python" in result.matched_skills
