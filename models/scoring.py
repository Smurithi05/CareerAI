"""
models/scoring.py
====================
MODULE 3 (AI Job Matching) + MODULE 4 (Skill Gap Analysis) core logic.

All scores produced here are ACADEMIC PROJECT METRICS meant to support
self-assessment and learning. They are explicitly NOT a scientifically
validated hiring/recruitment score, and the UI must say so.

Scoring formula (declared exactly as required by the project spec):

    Final Match Score = SEMANTIC_WEIGHT * semantic_similarity
                       + SKILL_OVERLAP_WEIGHT * skill_overlap_score

Both components are in [0, 1] and the final score is reported as a
percentage.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from config import (
    SEMANTIC_WEIGHT,
    SKILL_OVERLAP_WEIGHT,
    STRONG_MATCH_THRESHOLD,
    PARTIAL_MATCH_THRESHOLD,
)
from models.similarity import compute_pairwise_similarity, best_matches


@dataclass
class SkillGapItem:
    skill: str
    status: str          # "Strong Match" | "Partial Match" | "Missing"
    importance: str       # "High" | "Medium"
    similarity_score: float = 0.0
    matched_resume_skill: str = ""


@dataclass
class JobMatchResult:
    semantic_similarity: float
    skill_overlap_score: float
    final_score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    partial_skills: List[Dict] = field(default_factory=list)
    resume_skill_coverage: float = 0.0
    engine_name: str = ""


def compute_skill_overlap(resume_skills: List[str], job_skills: List[str]) -> float:
    """
    Simple, explainable set-overlap score:
        overlap = |resume_skills ∩ job_skills| / |job_skills|
    i.e. "of everything the job asks for, what fraction does the resume
    already state explicitly (exact/alias match)?"
    """
    if not job_skills:
        return 0.0
    resume_set = {s.lower() for s in resume_skills}
    job_set = {s.lower() for s in job_skills}
    overlap = resume_set.intersection(job_set)
    return len(overlap) / len(job_set)


def classify_skill_gaps(
    resume_skills: List[str],
    job_required_skills: List[str],
    job_preferred_skills: List[str],
) -> List[SkillGapItem]:
    """
    For every skill the job asks for (required = High importance, preferred
    = Medium importance), classify it as Strong / Partial / Missing based on:
      - exact match against resume skill list -> Strong
      - else, best semantic similarity against resume skills:
            >= STRONG_MATCH_THRESHOLD  -> Strong
            >= PARTIAL_MATCH_THRESHOLD -> Partial
            otherwise                  -> Missing
    """
    resume_set_lower = {s.lower(): s for s in resume_skills}
    results: List[SkillGapItem] = []

    all_job_skills = [(s, "High") for s in job_required_skills] + [
        (s, "Medium") for s in job_preferred_skills
    ]

    for job_skill, importance in all_job_skills:
        if job_skill.lower() in resume_set_lower:
            results.append(
                SkillGapItem(
                    skill=job_skill,
                    status="Strong Match",
                    importance=importance,
                    similarity_score=1.0,
                    matched_resume_skill=resume_set_lower[job_skill.lower()],
                )
            )
            continue

        if resume_skills:
            matches = best_matches([job_skill], resume_skills)
            _, best_resume_skill, score = matches[0]
        else:
            best_resume_skill, score = None, 0.0

        if score >= STRONG_MATCH_THRESHOLD:
            status = "Strong Match"
        elif score >= PARTIAL_MATCH_THRESHOLD:
            status = "Partial Match"
        else:
            status = "Missing"

        results.append(
            SkillGapItem(
                skill=job_skill,
                status=status,
                importance=importance,
                similarity_score=round(score, 3),
                matched_resume_skill=best_resume_skill or "",
            )
        )

    return results


def compute_job_match(
    resume_profile: Dict,
    job_profile: Dict,
) -> JobMatchResult:
    """
    Top-level Module 3 function: combines semantic similarity (over the
    full resume text vs full JD text) with explicit skill overlap into the
    transparent, documented Final Match Score.
    """
    from models.embeddings import get_engine_name

    resume_text = resume_profile.get("cleaned_text", "")
    job_text = job_profile.get("cleaned_text", "")

    semantic_sim = compute_pairwise_similarity(resume_text, job_text)

    resume_skills = resume_profile.get("skills", [])
    job_required = job_profile.get("required_skills", [])
    job_preferred = job_profile.get("preferred_skills", [])
    all_job_skills = list(dict.fromkeys(job_required + job_preferred))

    skill_overlap = compute_skill_overlap(resume_skills, all_job_skills)

    final_score = (SEMANTIC_WEIGHT * semantic_sim) + (SKILL_OVERLAP_WEIGHT * skill_overlap)

    gap_items = classify_skill_gaps(resume_skills, job_required, job_preferred)
    matched = [g.skill for g in gap_items if g.status == "Strong Match"]
    partial = [
        {"skill": g.skill, "matched_resume_skill": g.matched_resume_skill, "score": g.similarity_score}
        for g in gap_items
        if g.status == "Partial Match"
    ]
    missing = [g.skill for g in gap_items if g.status == "Missing"]

    resume_coverage = (
        len(matched) / len(all_job_skills) if all_job_skills else 0.0
    )

    return JobMatchResult(
        semantic_similarity=round(semantic_sim, 4),
        skill_overlap_score=round(skill_overlap, 4),
        final_score=round(final_score, 4),
        matched_skills=matched,
        missing_skills=missing,
        partial_skills=partial,
        resume_skill_coverage=round(resume_coverage, 4),
        engine_name=get_engine_name(),
    )


# ---------------------------------------------------------------------------
# Learning recommendations for skill-gap items (rule-based knowledge base)
# ---------------------------------------------------------------------------
SKILL_RECOMMENDATIONS = {
    "REST API": "Learn HTTP methods, REST architecture, JSON, and API authentication; build a small Flask/FastAPI service exposing CRUD endpoints.",
    "Docker": "Learn images vs containers, Dockerfile basics, and docker-compose; containerize one of your existing projects.",
    "Spring Boot": "Learn dependency injection, REST controllers, and Spring Data JPA; build a small CRUD REST API in Spring Boot.",
    "Machine Learning": "Revise supervised learning basics (regression/classification), model evaluation metrics, and scikit-learn; build a small classifier on a public dataset.",
    "Deep Learning": "Learn neural network fundamentals (forward/back-prop), and build a small image classifier using TensorFlow/Keras or PyTorch.",
    "Kubernetes": "Learn pods, deployments, and services; deploy a containerized app to a local Minikube cluster.",
    "AWS": "Learn core services (EC2, S3, IAM) and deploy a simple web app using the AWS free tier.",
    "React": "Learn components, hooks (useState/useEffect), and props/state; build a small single-page app.",
    "SQL": "Practice joins, aggregations, and subqueries; solve query problems on a sample database (e.g. SQLite).",
    "Git": "Learn branching, merging, and pull-request workflows; contribute to a small open-source or personal repo.",
    "Data Structures": "Revise arrays, linked lists, trees, and hash maps; solve 20-30 practice problems.",
    "Algorithms": "Revise sorting, searching, recursion, and complexity analysis; practice on a coding platform.",
    "Django": "Learn MVT architecture, models/migrations, and Django REST Framework; build a small CRUD web app.",
    "Flask": "Learn routing, templates, and request handling; build a small web API.",
    "Node.js": "Learn the event loop, Express.js routing, and middleware; build a small backend service.",
    "MongoDB": "Learn documents/collections, CRUD operations, and aggregation pipelines; build a small app using MongoDB as the datastore.",
}

DEFAULT_RECOMMENDATION_TEMPLATE = (
    "Study the fundamentals of {skill}, work through a beginner tutorial, "
    "and build one small hands-on project that uses it."
)


def get_recommendation(skill: str) -> str:
    return SKILL_RECOMMENDATIONS.get(skill, DEFAULT_RECOMMENDATION_TEMPLATE.format(skill=skill))
