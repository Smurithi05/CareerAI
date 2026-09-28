"""
utils/session_state.py
=========================
Central place defining the Streamlit `session_state` keys shared across
pages, so pages don't silently diverge on key names. Streamlit's
session_state is what lets one page's output (e.g. Resume Analyzer) be
consumed by another page (e.g. Job Matcher) within the same browser
session, in addition to the permanent SQLite record.
"""

import streamlit as st

DEFAULTS = {
    "user_id": None,
    "candidate_name": None,
    "resume_profile": None,
    "resume_analysis_id": None,
    "job_profile": None,
    "job_analysis_id": None,
    "match_result": None,
    "skill_gap_items": None,
    "interview_questions": None,
    "interview_session_id": None,
    "interview_answers": {},       # {question_index: answer_text}
    "interview_results": None,     # list of {"question":..., "evaluation":...}
    "interview_summary": None,
    "roadmap": None,
}


def init_session_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session_state():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
