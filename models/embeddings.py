"""
models/embeddings.py
======================
Embedding engine abstraction with automatic fallback.

PRIMARY engine : sentence-transformers ("all-MiniLM-L6-v2") — a free, local,
                 pre-trained transformer model (no API key, no cost). It
                 produces dense semantic embeddings that capture MEANING,
                 not just keyword overlap.

FALLBACK engine: TF-IDF vectorization (scikit-learn) — used automatically
                 if sentence-transformers / its model weights are not
                 available (e.g. first run without internet access to
                 download the model). TF-IDF is a classic, purely
                 statistical bag-of-words representation; it does not
                 capture semantic meaning as well, but keeps the whole
                 application FUNCTIONAL offline.

The active engine name is exposed via `get_engine_name()` so the UI can
transparently tell the user which method produced a given score — this is
an explicit project requirement (no silent/misleading claims about which
AI technique is running).
"""

from typing import List, Optional
import numpy as np

from config import SENTENCE_TRANSFORMER_MODEL


class EmbeddingEngine:
    """
    Wraps either a SentenceTransformer model or a TF-IDF vectorizer behind
    one common `.encode(texts) -> np.ndarray` interface.
    """

    def __init__(self, model_name: str = SENTENCE_TRANSFORMER_MODEL):
        self.model_name = model_name
        self._st_model = None
        self._tfidf_vectorizer = None
        self.engine_name = "Uninitialized"
        self._load()

    # -- loading -----------------------------------------------------------
    def _load(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            self._st_model = SentenceTransformer(self.model_name)
            self.engine_name = f"Sentence Transformer ({self.model_name})"
        except Exception:
            # Any failure (not installed, no internet, corrupted cache, etc.)
            # silently and safely degrades to the TF-IDF fallback so the
            # app keeps working end-to-end.
            self._st_model = None
            self.engine_name = "TF-IDF Fallback"

    def is_transformer_active(self) -> bool:
        return self._st_model is not None

    # -- encoding ------------------------------------------------------------
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode a list of texts into vectors.
        NOTE: when using the TF-IDF fallback, the vectorizer must be FIT on
        the given batch of texts (since TF-IDF is corpus-relative). Callers
        should therefore pass ALL texts they want to compare in one call
        when using this method directly, OR use `similarity.py` helpers
        which handle this correctly.
        """
        if not texts:
            return np.zeros((0, 1))

        if self._st_model is not None:
            return self._st_model.encode(texts, show_progress_bar=False)

        # TF-IDF fallback: fit fresh on this batch (keeps things simple and
        # avoids stale-vocabulary issues across unrelated comparisons).
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        matrix = self._tfidf_vectorizer.fit_transform(texts)
        return matrix.toarray()


_ENGINE_SINGLETON: Optional[EmbeddingEngine] = None


def get_embedding_engine() -> EmbeddingEngine:
    """Return a process-wide singleton so the (possibly large) model is loaded once."""
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        _ENGINE_SINGLETON = EmbeddingEngine()
    return _ENGINE_SINGLETON


def get_engine_name() -> str:
    return get_embedding_engine().engine_name
