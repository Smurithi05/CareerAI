"""
utils/file_utils.py
======================
Small helpers for file validation used by the Streamlit upload widgets.
"""

from typing import Optional

ALLOWED_EXTENSIONS = (".pdf", ".docx")
MAX_FILE_SIZE_MB = 10


def is_allowed_resume_file(filename: str) -> bool:
    return filename.lower().endswith(ALLOWED_EXTENSIONS)


def validate_file_size(file_bytes: bytes, max_mb: int = MAX_FILE_SIZE_MB) -> Optional[str]:
    """Returns an error message string if the file is too large, else None."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        return f"File is too large ({size_mb:.1f} MB). Please upload a file under {max_mb} MB."
    return None
