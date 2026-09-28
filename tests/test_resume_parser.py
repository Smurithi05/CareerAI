"""
tests/test_resume_parser.py
==============================
Unit tests for nlp/resume_parser.py.

We avoid depending on real binary PDF/DOCX fixture files for the section/
field-extraction tests (keeps the repo lightweight); instead we test the
pure-text functions directly, and separately verify that unsupported file
types are correctly rejected.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from nlp.resume_parser import (
    extract_text,
    extract_name,
    extract_contact_info,
    extract_education,
    split_into_sections,
    ResumeParsingError,
)


SAMPLE_RESUME_TEXT = """John Doe
john.doe@example.com
9876543210

EDUCATION
B.Tech in Information Technology, XYZ University, 2024

TECHNICAL SKILLS
Python, Java, SQL, Git, Machine Learning

PROJECTS
Built a resume analyzer using Python and NLP techniques.
Developed a college management system using Java and MySQL.

INTERNSHIPS
Software Development Intern at ABC Corp, Summer 2023

CERTIFICATIONS
AWS Certified Cloud Practitioner
"""


def test_extract_text_rejects_unsupported_extension():
    with pytest.raises(ResumeParsingError):
        extract_text(b"dummy content", "resume.txt")


def test_extract_name_from_header():
    header = "John Doe\njohn.doe@example.com\n9876543210"
    name = extract_name(header)
    assert name == "John Doe"


def test_extract_contact_info():
    contact = extract_contact_info(SAMPLE_RESUME_TEXT)
    assert contact["email"] == "john.doe@example.com"
    assert contact["phone"] is not None
    assert "9876543210" in contact["phone"]


def test_split_into_sections_detects_known_headers():
    sections = split_into_sections(SAMPLE_RESUME_TEXT)
    assert "education" in sections
    assert "skills" in sections
    assert "projects" in sections
    assert "python" in sections["skills"].lower()


def test_extract_education_finds_degree_line():
    sections = split_into_sections(SAMPLE_RESUME_TEXT)
    education = extract_education(sections["education"])
    assert any("b.tech" in e.lower() for e in education)
