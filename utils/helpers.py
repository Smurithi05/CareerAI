"""
utils/helpers.py
===================
Small shared helper functions used across multiple Streamlit pages.
"""

from typing import List


def pct(value: float) -> float:
    """Convert a 0-1 fraction to a 0-100 percentage, rounded to 1 decimal."""
    return round(max(0.0, min(1.0, value)) * 100, 1)


def score_label(score_out_of_10: float) -> str:
    """Human-readable label for a /10 score, used in feedback text."""
    if score_out_of_10 >= 8:
        return "Excellent"
    if score_out_of_10 >= 6.5:
        return "Good"
    if score_out_of_10 >= 5:
        return "Fair"
    if score_out_of_10 >= 3:
        return "Needs Improvement"
    return "Weak"


def truncate(text: str, max_len: int = 120) -> str:
    text = text or ""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def safe_list(value) -> List:
    """Ensure a value is always returned as a list (never None)."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def format_skill_list(skills: List[str], max_display: int = 25) -> str:
    if not skills:
        return "None"
    shown = skills[:max_display]
    suffix = f" (+{len(skills) - max_display} more)" if len(skills) > max_display else ""
    return ", ".join(shown) + suffix
