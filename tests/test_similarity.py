"""
tests/test_similarity.py
===========================
Unit tests for models/similarity.py.

These tests work correctly with EITHER the sentence-transformer engine or
the TF-IDF fallback (whichever is available in the environment), since we
only assert relative/ordinal relationships rather than exact scores.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.similarity import compute_pairwise_similarity, compute_similarity_matrix, best_matches


def test_similarity_of_identical_text_is_high():
    score = compute_pairwise_similarity("Python developer with Flask experience", "Python developer with Flask experience")
    assert score > 0.9


def test_similar_text_scores_higher_than_unrelated_text():
    base = "Experienced Python developer skilled in Flask and REST APIs"
    similar = "Skilled Python programmer with REST API and Flask background"
    unrelated = "Professional chef specializing in Italian pasta dishes"

    sim_score = compute_pairwise_similarity(base, similar)
    unrelated_score = compute_pairwise_similarity(base, unrelated)

    assert sim_score > unrelated_score


def test_empty_text_returns_zero():
    assert compute_pairwise_similarity("", "something") == 0.0
    assert compute_pairwise_similarity("something", "") == 0.0


def test_similarity_matrix_shape():
    matrix = compute_similarity_matrix(["Python", "Java"], ["Python programming", "Cooking", "Java development"])
    assert matrix.shape == (2, 3)


def test_best_matches_picks_expected_pair():
    results = best_matches(["Python"], ["Java development", "Python programming language"])
    item_a, best_b, score = results[0]
    assert item_a == "Python"
    assert best_b == "Python programming language"
