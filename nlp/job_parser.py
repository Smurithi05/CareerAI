"""
nlp/job_parser.py
===================
Job Description Intelligence module (MODULE 2).

Extracts a structured job profile from a free-text job description:
role title, required skills, preferred/nice-to-have skills, tools,
experience requirement, education requirement, and generic role keywords.

Like the resume parser, this is rule-based NLP (keyword + regex heuristics)
layered on top of the shared skill dictionary — not a trained classifier.
"""

import re
from typing import Dict, List

from nlp.text_preprocessor import clean_text, keyword_set
from nlp.skill_extractor import SkillExtractor

PREFERRED_MARKERS = [
    "preferred", "nice to have", "good to have", "bonus", "plus point",
    "added advantage", "desirable",
]
REQUIRED_MARKERS = [
    "required", "must have", "mandatory", "requirements", "responsibilities",
    "essential", "you should have", "qualifications",
]

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "bachelor", "b.e", "bachelor's degree", "m.tech",
    "master's degree", "mca", "bca", "computer science", "engineering degree",
    "information technology", "any graduate",
]

ROLE_KEYWORDS_BANK = [
    "software developer", "software engineer", "data analyst", "data scientist",
    "machine learning engineer", "ml engineer", "python developer",
    "web developer", "full stack developer", "front end developer",
    "back end developer", "backend developer", "frontend developer",
    "devops engineer", "qa engineer", "test engineer", "cloud engineer",
    "database administrator", "business analyst", "product manager",
    "ui/ux designer", "mobile app developer", "android developer",
    "ios developer", "system administrator", "network engineer",
]


class JobDescriptionParsingError(Exception):
    pass


def _split_into_lines(text: str) -> List[str]:
    return [l.strip() for l in text.split("\n") if l.strip()]


def extract_role_title(text: str, fallback: str = "Not Specified") -> str:
    lower = text.lower()

    for role in ROLE_KEYWORDS_BANK:
        if role in lower:
            return role.title()

    # Fallback: first non-empty short line is often the job title when
    # pasted from a job posting.
    lines = _split_into_lines(text)
    if lines and len(lines[0].split()) <= 8:
        return lines[0]
    return fallback


def _line_marked_as(line: str, markers: List[str]) -> bool:
    low = line.lower()
    return any(m in low for m in markers)


def extract_experience_requirement(text: str) -> List[str]:
    matches = re.findall(
        r"(\d+(?:\.\d+)?\s*[-–to]{0,4}\s*\d*\+?\s*years?)",
        text.lower(),
    )
    cleaned = sorted(set(m.strip() for m in matches if m.strip()))
    return cleaned


def extract_education_requirement(text: str) -> List[str]:
    low = text.lower()
    found = [kw for kw in EDUCATION_KEYWORDS if kw in low]
    # de-duplicate while keeping a readable canonical form
    result = []
    seen = set()
    for kw in found:
        key = kw.replace(".", "").replace("'s degree", "")
        if key not in seen:
            seen.add(key)
            result.append(kw)
    return result


def extract_role_keywords(text: str, top_n: int = 15) -> List[str]:
    """
    A lightweight 'keyword importance' extractor: counts frequency of
    meaningful (non-stopword) tokens as a rough proxy for what the JD
    emphasizes. This is a simple frequency-based NLP technique (not TF-IDF
    across a corpus, since we only have one document here).
    """
    tokens = list(keyword_set(text))
    freq: Dict[str, int] = {}
    low_text = text.lower()
    for tok in tokens:
        freq[tok] = low_text.count(tok)
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, c in ranked[:top_n] if len(w) > 2]


def parse_job_description(raw_text: str, skill_extractor: SkillExtractor) -> Dict:
    """
    Full Module 2 pipeline: raw JD text -> structured job profile dict.
    """
    if not raw_text or not raw_text.strip():
        raise JobDescriptionParsingError("Job description text is empty.")

    cleaned = clean_text(raw_text)
    lines = _split_into_lines(cleaned)

    required_lines, preferred_lines, general_lines = [], [], []
    mode = "general"
    for line in lines:
        if _line_marked_as(line, REQUIRED_MARKERS):
            mode = "required"
        elif _line_marked_as(line, PREFERRED_MARKERS):
            mode = "preferred"

        if mode == "required":
            required_lines.append(line)
        elif mode == "preferred":
            preferred_lines.append(line)
        else:
            general_lines.append(line)

    required_text = "\n".join(required_lines) if required_lines else cleaned
    preferred_text = "\n".join(preferred_lines)

    required_skill_matches = skill_extractor.extract(required_text)
    preferred_skill_matches = skill_extractor.extract(preferred_text) if preferred_text else []

    required_skill_names = {m.skill for m in required_skill_matches}
    # A skill only counted as "preferred" if it wasn't already required
    preferred_skill_names = {m.skill for m in preferred_skill_matches} - required_skill_names

    # If no explicit preferred section existed, treat all detected skills as required.
    if not preferred_text:
        all_matches = skill_extractor.extract(cleaned)
        required_skill_names = {m.skill for m in all_matches}
        preferred_skill_names = set()

    tools = sorted(
        {m.skill for m in skill_extractor.extract(cleaned) if m.category == "Tool"}
    )

    profile = {
        "role": extract_role_title(cleaned),
        "required_skills": sorted(required_skill_names),
        "preferred_skills": sorted(preferred_skill_names),
        "tools": tools,
        "experience": extract_experience_requirement(cleaned),
        "education_requirements": extract_education_requirement(cleaned),
        "role_keywords": extract_role_keywords(cleaned),
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "word_count": len(cleaned.split()),
    }
    return profile
