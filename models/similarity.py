"""
models/similarity.py
======================
Cosine-similarity utilities built on top of the embedding engine
(models/embeddings.py). Works identically whether the active engine is
the sentence-transformer model or the TF-IDF fallback, because both
expose the same `.encode()` interface.
"""

from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from models.embeddings import get_embedding_engine


def compute_pairwise_similarity(text_a: str, text_b: str) -> float:
    """
    Compute a single semantic similarity score in [0, 1] between two texts.
    """
    text_a = (text_a or "").strip()
    text_b = (text_b or "").strip()
    if not text_a or not text_b:
        return 0.0

    engine = get_embedding_engine()
    vectors = engine.encode([text_a, text_b])
    if vectors.shape[0] < 2:
        return 0.0

    sim = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    # Clip into [0, 1] — TF-IDF cosine sim is already >=0; transformer
    # cosine sim can occasionally be slightly negative for unrelated text.
    return float(max(0.0, min(1.0, sim)))


def compute_similarity_matrix(texts_a: List[str], texts_b: List[str]) -> np.ndarray:
    """
    Compute an (len(texts_a) x len(texts_b)) cosine similarity matrix.
    Useful for comparing every resume skill/sentence against every JD
    skill/sentence at once (used in skill-gap partial-match detection).
    """
    if not texts_a or not texts_b:
        return np.zeros((len(texts_a), len(texts_b)))

    engine = get_embedding_engine()
    all_texts = list(texts_a) + list(texts_b)
    all_vectors = engine.encode(all_texts)

    vec_a = all_vectors[: len(texts_a)]
    vec_b = all_vectors[len(texts_a):]
    matrix = cosine_similarity(vec_a, vec_b)
    return np.clip(matrix, 0.0, 1.0)


def best_matches(texts_a: List[str], texts_b: List[str]) -> List[Tuple[str, str, float]]:
    """
    For each item in texts_a, find its single best-matching item in texts_b
    and the similarity score. Returns list of (item_a, best_item_b, score).
    """
    if not texts_a or not texts_b:
        return [(a, None, 0.0) for a in texts_a]

    matrix = compute_similarity_matrix(texts_a, texts_b)
    results = []
    for i, a in enumerate(texts_a):
        j = int(np.argmax(matrix[i]))
        results.append((a, texts_b[j], float(matrix[i][j])))
    return results
