"""
interview/feedback.py
========================
Aggregates per-question AnswerEvaluation results into an overall interview
performance summary: total score, category-wise breakdown (Technical vs
HR vs Behavioral vs Scenario-Based vs Project-Based), and a ranked list of
"weak areas" used later by the roadmap generator (Module 7).
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from interview.answer_evaluator import AnswerEvaluation


@dataclass
class InterviewSummary:
    overall_score: float
    total_questions: int
    category_scores: Dict[str, float] = field(default_factory=dict)
    weak_concepts: List[str] = field(default_factory=list)
    weak_categories: List[str] = field(default_factory=list)
    overall_feedback: str = ""


def summarize_interview(
    results: List[Dict],
) -> InterviewSummary:
    """
    `results` is a list of dicts:
        {"question": InterviewQuestion, "evaluation": AnswerEvaluation}
    """
    if not results:
        return InterviewSummary(overall_score=0.0, total_questions=0, overall_feedback="No answers submitted.")

    category_totals: Dict[str, List[float]] = defaultdict(list)
    concept_miss_counter: Dict[str, int] = defaultdict(int)
    overall_scores = []

    for r in results:
        q = r["question"]
        ev: AnswerEvaluation = r["evaluation"]
        overall_scores.append(ev.overall_score)
        category_totals[q.category].append(ev.overall_score)
        for concept in ev.missing_concepts:
            concept_miss_counter[concept] += 1

    overall_score = round(sum(overall_scores) / len(overall_scores), 2)

    category_scores = {
        cat: round(sum(scores) / len(scores), 2) for cat, scores in category_totals.items()
    }

    weak_categories = sorted(category_scores, key=lambda c: category_scores[c])[:2]
    weak_concepts = sorted(concept_miss_counter, key=lambda c: concept_miss_counter[c], reverse=True)[:8]

    if overall_score >= 8:
        tone = "Excellent overall performance."
    elif overall_score >= 6:
        tone = "Good performance with some room for improvement."
    elif overall_score >= 4:
        tone = "Fair performance — several concepts need reinforcement."
    else:
        tone = "This interview highlighted significant gaps that need focused preparation."

    feedback = (
        f"{tone} You answered {len(results)} question(s) with an average score of "
        f"{overall_score}/10. Weakest area(s): {', '.join(weak_categories) if weak_categories else 'None'}. "
        f"This is an AI-assisted academic assessment, not a substitute for a real interview panel's judgement."
    )

    return InterviewSummary(
        overall_score=overall_score,
        total_questions=len(results),
        category_scores=category_scores,
        weak_concepts=weak_concepts,
        weak_categories=weak_categories,
        overall_feedback=feedback,
    )
