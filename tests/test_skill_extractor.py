"""
tests/test_skill_extractor.py
================================
Unit tests for nlp/skill_extractor.py — dictionary/alias/fuzzy matching.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SKILLS_CSV
from nlp.skill_extractor import SkillExtractor


extractor = SkillExtractor(str(SKILLS_CSV))


def test_exact_match_detects_python():
    skills = extractor.extract_names("I have strong experience with Python and SQL.")
    assert "Python" in skills
    assert "SQL" in skills


def test_alias_match_detects_javascript_via_js():
    skills = extractor.extract_names("Worked extensively with JS and React.js for the frontend.")
    assert "JavaScript" in skills
    assert "React" in skills


def test_symbol_skills_like_cplusplus_and_csharp():
    skills = extractor.extract_names("Proficient in C++ and C# for systems programming.")
    assert "C++" in skills
    assert "C#" in skills


def test_no_false_positive_on_unrelated_text():
    skills = extractor.extract_names("I enjoy painting and playing the guitar on weekends.")
    assert "Python" not in skills
    assert "Java" not in skills


def test_fuzzy_match_handles_minor_typo():
    skills = extractor.extract_names("Experienced in Djnago web framework.", fuzzy=True, fuzzy_cutoff=0.8)
    assert "Django" in skills
