"""
pages/1_Resume_Analyzer.py
=============================
MODULE 1 UI: upload a resume (PDF/DOCX) and display the structured
candidate profile extracted by nlp/resume_parser.py.
"""

import streamlit as st

from config import SKILLS_CSV, APP_ICON
from database.database import get_or_create_user, save_resume_analysis
from nlp.resume_parser import parse_resume, ResumeParsingError
from nlp.skill_extractor import get_skill_extractor
from utils.file_utils import is_allowed_resume_file, validate_file_size
from utils.session_state import init_session_state
from utils.helpers import format_skill_list
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_metric_card, render_info_card, render_ai_badge, render_footer, skill_chips,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Resume Analyzer | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("resume_analyzer")

render_page_header("📄", "Resume Analyzer", "MODULE 1 — Resume Intelligence",
                    "Upload your resume and CareerAI will extract, structure, and skill-tag its contents.")
render_ai_badge("NLP ANALYSIS")

with st.expander("ℹ️ How this works (click to expand)"):
    st.markdown(
        """
        1. Your PDF/DOCX is read locally using **pypdf** / **python-docx** — nothing leaves your machine.
        2. The extracted text is cleaned and normalized (rule-based NLP preprocessing).
        3. Resume sections (Education, Projects, Internships, Certifications) are
           located using **keyword + layout heuristics**, not fixed templates.
        4. Skills are identified using a **maintainable skill dictionary**
           (`data/skills.csv`) with alias + fuzzy matching — this is a
           lexical NLP technique, not a trained ML classifier.
        """
    )

render_section_header("Upload Your Resume", 1)
st.markdown(
    """<div class="cai-card" style="text-align:center; padding:34px 20px;">
    <div style="font-size:2.4rem;">📄</div>
    <h4>Drop your resume here or browse files</h4>
    <p style="font-size:0.85rem; color:#9aa4c4;">Supported formats: PDF · DOCX</p>
    </div>""",
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"], label_visibility="collapsed")

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name

    size_error = validate_file_size(file_bytes)
    if size_error:
        st.error(size_error)
    elif not is_allowed_resume_file(filename):
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
    else:
        try:
            with st.spinner("🧠 Extracting and analyzing your resume with NLP..."):
                extractor = get_skill_extractor(str(SKILLS_CSV))
                profile = parse_resume(file_bytes, filename, extractor)

            st.session_state["resume_profile"] = profile
            st.session_state["candidate_name"] = profile["name"]
            user_id = get_or_create_user(profile["name"], profile.get("email"))
            st.session_state["user_id"] = user_id
            resume_analysis_id = save_resume_analysis(user_id, profile)
            st.session_state["resume_analysis_id"] = resume_analysis_id

            st.success(f"✅ Resume parsed successfully for **{profile['name']}**.")

        except ResumeParsingError as e:
            st.error(f"⚠️ Could not process this resume: {e}")
        except Exception:
            st.error(
                "⚠️ Something went wrong while analyzing this resume. "
                "Please make sure it is a valid, non-corrupted PDF or DOCX file."
            )

profile = st.session_state.get("resume_profile")

if profile:
    render_section_header(f"Candidate Profile — {profile['name']}", 2)

    m1, m2, m3 = st.columns(3)
    render_metric_card(m1, str(len(profile["skills"])), "Skills Detected")
    render_metric_card(m2, str(len(profile["projects"])), "Projects Detected")
    render_metric_card(m3, str(profile["word_count"]), "Word Count")

    st.markdown("")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🧠 Skills", "🎓 Education", "💼 Projects & Internships", "📜 Certifications", "📝 Raw Extracted Text"]
    )

    with tab1:
        if profile["skills_by_category"]:
            for category, skills in sorted(profile["skills_by_category"].items()):
                st.markdown(f"**{category}**")
                skill_chips(skills, variant="matched")
        else:
            render_info_card(
                "No skills were detected against the skill dictionary. "
                "Try adding a clear 'Technical Skills' section to your resume.",
                variant="warning",
            )

    with tab2:
        if profile["education"]:
            for e in profile["education"]:
                st.markdown(f"- {e}")
        else:
            render_info_card("No education entries were confidently detected.", variant="neutral")

    with tab3:
        st.markdown("**Projects**")
        if profile["projects"]:
            for p in profile["projects"]:
                st.markdown(f"- {p}")
        else:
            render_info_card("No projects were confidently detected.", variant="neutral")

        st.markdown("**Internships / Experience**")
        if profile["internships"]:
            for i in profile["internships"]:
                st.markdown(f"- {i}")
        else:
            render_info_card("No internship/experience entries were confidently detected.", variant="neutral")

        if profile.get("years_of_experience"):
            render_info_card(f"Detected experience mention: <b>{profile['years_of_experience']}</b>", variant="neutral")

    with tab4:
        if profile["certifications"]:
            for c in profile["certifications"]:
                st.markdown(f"- {c}")
        else:
            render_info_card("No certifications were confidently detected.", variant="neutral")

    with tab5:
        st.text_area("Cleaned extracted text", profile["cleaned_text"], height=300)

    render_info_card("➡️ Next step: go to <b>Job Matcher</b> in the sidebar to compare this resume against a target job description.", variant="success")
else:
    render_info_card("Upload a resume above to begin.", variant="warning")

render_footer()
