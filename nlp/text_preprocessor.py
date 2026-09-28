"""
nlp/text_preprocessor.py
=========================
Rule-based text cleaning and normalization utilities.

These functions are classic NLP *preprocessing* steps (not ML models).
They are used by both the resume parser and the job-description parser
so that downstream skill-extraction and similarity code always sees text
in a consistent, normalized form.
"""

import re
import unicodedata
from typing import List

# Lazy, optional spaCy load -------------------------------------------------
# spaCy is used for sentence segmentation / lemmatization / stopword removal.
# If the model is not installed, we fall back to lightweight regex-based
# alternatives so that the app NEVER crashes just because `en_core_web_sm`
# has not been downloaded yet.
_NLP = None
_SPACY_AVAILABLE = False

try:
    import spacy

    try:
        _NLP = spacy.load("en_core_web_sm")
        _SPACY_AVAILABLE = True
    except OSError:
        _NLP = None
        _SPACY_AVAILABLE = False
except ImportError:
    _NLP = None
    _SPACY_AVAILABLE = False


BASIC_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "to", "of", "in", "on", "at", "for", "with", "as",
    "by", "this", "that", "it", "from", "we", "you", "he", "she", "they",
    "i", "our", "your", "their", "will", "shall", "can", "could", "would",
    "should", "have", "has", "had", "do", "does", "did", "not", "no",
}


def is_spacy_available() -> bool:
    """Expose spaCy availability so the UI can display which NLP engine is active."""
    return _SPACY_AVAILABLE


def clean_text(text: str) -> str:
    """
    Normalize raw extracted text: fix unicode artifacts, collapse whitespace,
    strip control/bullet characters that commonly appear in PDF extraction.
    """
    if not text:
        return ""

    # Normalize unicode (handles ligatures like "ﬁ" -> "fi", smart quotes, etc.)
    text = unicodedata.normalize("NFKD", text)

    # Remove common bullet / control characters left over from PDF extraction
    text = re.sub(r"[•●▪○◦➤➢‣∙]", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)

    # Collapse multiple spaces/newlines but keep paragraph structure roughly
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = text.strip()
    return text


def normalize_for_matching(text: str) -> str:
    """
    A more aggressive normalization used specifically when comparing tokens
    against the skill dictionary (case-insensitive, punctuation-insensitive).
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\s]", " ", text)  # keep C++, C#, .NET style tokens
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text: str) -> List[str]:
    """Sentence segmentation, using spaCy if available, else a regex fallback."""
    text = clean_text(text)
    if not text:
        return []

    if _SPACY_AVAILABLE:
        doc = _NLP(text)
        return [s.text.strip() for s in doc.sents if s.text.strip()]

    # Fallback: naive split on sentence-ending punctuation / newlines
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str) -> List[str]:
    """Simple whitespace/punctuation tokenizer used for keyword coverage checks."""
    text = normalize_for_matching(text)
    return [t for t in text.split() if t]


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove a basic stopword list. Works with or without spaCy/NLTK installed."""
    return [t for t in tokens if t not in BASIC_STOPWORDS and len(t) > 1]


def lemmatize(text: str) -> str:
    """
    Lemmatize text using spaCy if available. Falls back to returning the
    lowercased text unchanged (still functional, just less normalized).
    """
    if _SPACY_AVAILABLE:
        doc = _NLP(text)
        return " ".join(tok.lemma_ for tok in doc if not tok.is_space)
    return text.lower()


def keyword_set(text: str) -> set:
    """Return a normalized, stopword-free set of tokens — used for keyword-coverage scoring."""
    return set(remove_stopwords(tokenize(text)))
