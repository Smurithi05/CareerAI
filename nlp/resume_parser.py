"""
nlp/resume_parser.py
======================
Resume Intelligence module (MODULE 1).

Pipeline:
  raw file (PDF/DOCX) -> raw text -> cleaned text -> section splitting
  -> skill extraction + rule-based field extraction -> structured profile (dict)

The section splitter is heuristic/rule-based (keyword + layout cues), which
is standard practice for resume parsers since resumes do not follow one
fixed schema. It is intentionally NOT hard-coded to exact resume templates.
"""

import io
import re
from typing import Dict, List, Optional

from nlp.text_preprocessor import clean_text, split_sentences
from nlp.skill_extractor import SkillExtractor


class ResumeParsingError(Exception):
    """Raised when a resume file cannot be read or contains no usable text."""


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ResumeParsingError(
            "PDF support library (pypdf) is not installed. Run: pip install pypdf"
        ) from e

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ResumeParsingError("This PDF is password-protected and cannot be read.")
        text_parts = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(text_parts)
    except ResumeParsingError:
        raise
    except Exception as e:
        raise ResumeParsingError(f"Could not read PDF file: {e}") from e

    if not text.strip():
        raise ResumeParsingError(
            "No extractable text was found in this PDF. It may be a scanned "
            "image without a text layer (OCR is not supported in this prototype)."
        )
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
    except ImportError as e:
        raise ResumeParsingError(
            "DOCX support library (python-docx) is not installed. Run: pip install python-docx"
        ) from e

    try:
        document = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs]
        # Also pull text out of tables (common in resume templates)
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
        text = "\n".join(paragraphs)
    except Exception as e:
        raise ResumeParsingError(f"Could not read DOCX file: {e}") from e

    if not text.strip():
        raise ResumeParsingError("No extractable text was found in this DOCX file.")
    return text


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Dispatch to the correct extractor based on file extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ResumeParsingError(
            "Unsupported file type. Please upload a resume in PDF (.pdf) or Word (.docx) format."
        )


# ---------------------------------------------------------------------------
# Section splitting (rule-based, keyword driven)
# ---------------------------------------------------------------------------
SECTION_HEADERS = {
    "education": ["education", "academic background", "academic qualification", "qualifications"],
    "skills": ["technical skills", "skills", "key skills", "core competencies"],
    "projects": ["projects", "academic projects", "personal projects", "major projects"],
    "internships": ["internship", "internships", "work experience", "professional experience", "experience"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "summary": ["summary", "objective", "career objective", "profile"],
}


def _find_section_boundaries(lines: List[str]) -> Dict[str, tuple]:
    """
    Scan lines and locate the start index of each known section header.
    A line is treated as a header if it is short, mostly title-case/uppercase,
    and matches (or closely matches) one of our known header keywords.
    """
    boundaries = {}
    for idx, line in enumerate(lines):
        stripped = line.strip().lower().strip(":")
        if not stripped or len(stripped) > 40:
            continue
        for section, keywords in SECTION_HEADERS.items():
            for kw in keywords:
                if stripped == kw or (stripped.startswith(kw) and len(stripped) <= len(kw) + 3):
                    boundaries.setdefault(section, idx)
    return boundaries


def split_into_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into named sections using detected header positions.
    Any text before the first detected header is treated as the 'header'
    (usually name / contact info / summary).
    """
    lines = text.split("\n")
    boundaries = _find_section_boundaries(lines)

    if not boundaries:
        return {"full_text": text}

    ordered = sorted(boundaries.items(), key=lambda kv: kv[1])
    sections: Dict[str, str] = {}
    sections["header"] = "\n".join(lines[: ordered[0][1]]).strip()

    for i, (section, start_idx) in enumerate(ordered):
        end_idx = ordered[i + 1][1] if i + 1 < len(ordered) else len(lines)
        content = "\n".join(lines[start_idx + 1 : end_idx]).strip()
        # merge if same section name appears twice (e.g. "experience" listed twice)
        if section in sections:
            sections[section] += "\n" + content
        else:
            sections[section] = content

    sections["full_text"] = text
    return sections


# ---------------------------------------------------------------------------
# Field extractors (rule-based / regex heuristics)
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?\d{10}\b")
DEGREE_KEYWORDS = [
    "b.tech", "btech", "bachelor of technology", "b.e", "be ", "bachelor of engineering",
    "m.tech", "mtech", "master of technology", "bsc", "b.sc", "msc", "m.sc",
    "mca", "bca", "mba", "phd", "diploma", "12th", "10th", "hsc", "ssc",
    "bachelor", "master",
]


def extract_name(header_text: str) -> Optional[str]:
    """
    Heuristic: the candidate's name is usually the first non-empty line of
    the resume that is not an email/phone/address and is reasonably short.
    """
    for line in header_text.split("\n"):
        candidate = line.strip()
        if not candidate:
            continue
        if EMAIL_RE.search(candidate) or PHONE_RE.search(candidate):
            continue
        if len(candidate.split()) <= 5 and len(candidate) <= 60:
            # Avoid lines that look like section headers or addresses
            if not any(ch.isdigit() for ch in candidate):
                return candidate
    return None


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def extract_education(section_text: str) -> List[str]:
    if not section_text:
        return []
    entries = []
    for line in section_text.split("\n"):
        line_clean = line.strip()
        if not line_clean:
            continue
        low = line_clean.lower()
        if any(kw in low for kw in DEGREE_KEYWORDS) or re.search(r"\b(19|20)\d{2}\b", low):
            entries.append(line_clean)
    return entries if entries else [l.strip() for l in section_text.split("\n") if l.strip()][:5]


def extract_bulleted_entries(section_text: str, max_items: int = 15) -> List[str]:
    """
    Generic helper: split a section (projects / internships / certifications)
    into discrete entries using bullet markers or blank-line/newline grouping.
    """
    if not section_text:
        return []
    # First try splitting on bullet-like markers already normalized upstream
    raw_lines = [l.strip("-•*● \t") for l in section_text.split("\n")]
    entries = [l.strip() for l in raw_lines if l.strip()]
    return entries[:max_items]


def extract_years_of_experience(text: str) -> Optional[str]:
    """Look for explicit experience mentions like '2 years of experience'."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(years|yrs)\b", text.lower())
    if match:
        return f"{match.group(1)} years"
    return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def parse_resume(file_bytes: bytes, filename: str, skill_extractor: SkillExtractor) -> Dict:
    """
    Full Module 1 pipeline: bytes -> structured candidate profile dict.

    Returns a dictionary matching the schema described in the project spec:
    {name, email, phone, education, skills, projects, internships,
     certifications, experience, years_of_experience, raw_text, sections}
    """
    raw_text = extract_text(file_bytes, filename)
    cleaned = clean_text(raw_text)
    sections = split_into_sections(cleaned)

    header_text = sections.get("header", cleaned[:300])
    name = extract_name(header_text) or "Candidate"
    contact = extract_contact_info(cleaned)

    education = extract_education(sections.get("education", ""))
    projects = extract_bulleted_entries(sections.get("projects", ""))
    internships = extract_bulleted_entries(
        sections.get("internships", sections.get("experience", ""))
    )
    certifications = extract_bulleted_entries(sections.get("certifications", ""))

    # Skills: run extraction over the WHOLE resume (not just the "skills"
    # section) because candidates often mention tools inside project
    # descriptions too.
    skill_matches = skill_extractor.extract(cleaned)
    skills = [m.skill for m in skill_matches]
    skills_by_category: Dict[str, List[str]] = {}
    for m in skill_matches:
        skills_by_category.setdefault(m.category, []).append(m.skill)

    years_exp = extract_years_of_experience(cleaned)

    word_count = len(cleaned.split())
    sentence_count = len(split_sentences(cleaned))

    profile = {
        "name": name,
        "email": contact["email"],
        "phone": contact["phone"],
        "education": education,
        "skills": skills,
        "skills_by_category": skills_by_category,
        "projects": projects,
        "internships": internships,
        "certifications": certifications,
        "years_of_experience": years_exp,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "sections_detected": [s for s in sections.keys() if s not in ("full_text", "header")],
    }
    return profile
