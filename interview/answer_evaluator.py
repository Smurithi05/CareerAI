"""
interview/answer_evaluator.py
================================
MODULE 6: Interview Answer Evaluation.

IMPORTANT ACADEMIC DISCLAIMER (also shown in the UI):
This module produces an AI-ASSISTED ACADEMIC ASSESSMENT using NLP
similarity techniques. It is NOT equivalent to a human interviewer's
judgement and does not assess tone, confidence, body language, or
genuine domain depth the way a real interview panel would.

Scoring dimensions (each /10):
  1. Relevance          — semantic similarity between the answer and the
                           question + its expected concept list.
  2. Concept Coverage   — fraction of the question's "expected concepts"
                           that appear (exactly or as close paraphrase)
                           in the answer.
  3. Completeness       — a length/structure heuristic (very short answers
                           are penalized; reasonably developed answers with
                           multiple sentences score higher).

Overall = weighted average of the three (weights in config.ANSWER_WEIGHTS).
"""

from dataclasses import dataclass, field
from typing import Dict, List

from config import ANSWER_WEIGHTS
from nlp.text_preprocessor import keyword_set, split_sentences
from models.similarity import compute_pairwise_similarity


@dataclass
class AnswerEvaluation:
    relevance_score: float          # /10
    concept_coverage_score: float   # /10
    completeness_score: float       # /10
    overall_score: float            # /10
    matched_concepts: List[str] = field(default_factory=list)
    missing_concepts: List[str] = field(default_factory=list)
    word_count: int = 0
    sentence_count: int = 0
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)


def _score_relevance(question: str, concepts: List[str], answer: str) -> float:
    """Semantic similarity between the answer and (question + concept list) scaled to /10."""
    reference_text = question + ". Key ideas: " + ", ".join(concepts)
    sim = compute_pairwise_similarity(reference_text, answer)
    return round(sim * 10, 2)


def _score_concept_coverage(concepts: List[str], answer: str) -> (float, List[str], List[str]):
    """
    Checks how many of the expected concept keywords/phrases are present in
    the answer (token-overlap based — an explicit, explainable NLP
    technique distinct from the semantic-similarity relevance score above).
    """
    if not concepts:
        return 10.0, [], []  # no concepts defined -> don't penalize

    answer_tokens = keyword_set(answer)
    matched, missing = [], []
    for concept in concepts:
        concept_tokens = keyword_set(concept)
        if not concept_tokens:
            continue
        overlap = concept_tokens.intersection(answer_tokens)
        # Consider it "covered" if at least half of the concept's own
        # tokens (or at least one token, for single-word concepts) appear.
        threshold = max(1, len(concept_tokens) // 2)
        if len(overlap) >= threshold:
            matched.append(concept)
        else:
            missing.append(concept)

    coverage_ratio = len(matched) / len(concepts) if concepts else 1.0
    return round(coverage_ratio * 10, 2), matched, missing


def _score_completeness(answer: str) -> float:
    """
    Heuristic completeness score based on answer length and structure.
    Not a measure of correctness — purely "did the candidate elaborate
    enough to be evaluated meaningfully".
    """
    words = answer.split()
    word_count = len(words)
    sentences = split_sentences(answer)
    sentence_count = len(sentences)

    if word_count == 0:
        return 0.0
    if word_count < 8:
        base = 2.0
    elif word_count < 20:
        base = 5.0
    elif word_count < 40:
        base = 7.5
    elif word_count < 100:
        base = 9.0
    else:
        base = 10.0

    # Small bonus for multi-sentence structure (suggests explanation, not
    # just a one-line keyword dump), capped at 10.
    if sentence_count >= 3:
        base = min(10.0, base + 0.5)

    return round(base, 2)


def evaluate_answer(question: str, concepts: List[str], answer: str) -> AnswerEvaluation:
    """
    Full Module 6 pipeline for a single question/answer pair.
    """
    answer = (answer or "").strip()
    word_count = len(answer.split())
    sentence_count = len(split_sentences(answer))

    if not answer:
        return AnswerEvaluation(
            relevance_score=0.0,
            concept_coverage_score=0.0,
            completeness_score=0.0,
            overall_score=0.0,
            matched_concepts=[],
            missing_concepts=list(concepts),
            word_count=0,
            sentence_count=0,
            strengths=[],
            improvements=["No answer was provided for this question."],
        )

    relevance = _score_relevance(question, concepts, answer)
    coverage, matched_concepts, missing_concepts = _score_concept_coverage(concepts, answer)
    completeness = _score_completeness(answer)

    overall = (
        ANSWER_WEIGHTS["relevance"] * relevance
        + ANSWER_WEIGHTS["concept_coverage"] * coverage
        + ANSWER_WEIGHTS["completeness"] * completeness
    )
    overall = round(overall, 2)

    strengths, improvements = [], []
    if relevance >= 7:
        strengths.append("Your answer stayed closely on-topic and relevant to the question asked.")
    if coverage >= 7:
        strengths.append("You covered most of the key concepts expected for this question.")
    if completeness >= 7:
        strengths.append("The answer was well-developed with sufficient explanation.")

    if relevance < 5:
        improvements.append("Try to directly address what the question is asking before adding extra detail.")
    if coverage < 5 and missing_concepts:
        improvements.append(
            "Consider mentioning: " + ", ".join(missing_concepts[:5]) + "."
        )
    if completeness < 5:
        improvements.append("Expand your answer with a concrete example or a short explanation of your reasoning.")
    if not strengths:
        strengths.append("You attempted the question — focus on structuring your answer around the core concept next time.")

    return AnswerEvaluation(
        relevance_score=relevance,
        concept_coverage_score=coverage,
        completeness_score=completeness,
        overall_score=overall,
        matched_concepts=matched_concepts,
        missing_concepts=missing_concepts,
        word_count=word_count,
        sentence_count=sentence_count,
        strengths=strengths,
        improvements=improvements,
    )
