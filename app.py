"""
app.py
========
CareerAI — Main Streamlit entry point (Home page).

Run with:
    streamlit run app.py

This file wires up:
  - page config / global styling (utils/theme.py design system)
  - one-time app initialization (DB tables, NLP engines)
  - the Home page hero + AI pipeline preview + navigation
  - the sidebar system-status panel (shows which NLP/semantic engine is
    active, so the offline-fallback behaviour is transparent to the user)

The rest of the application lives in Streamlit's native multipage
`pages/` folder, which is automatically picked up and listed in the
sidebar navigation by Streamlit.
"""

import streamlit as st

from config import APP_TITLE, APP_ICON, SKILLS_CSV
from database.database import init_db
from nlp.skill_extractor import get_skill_extractor
from nlp.text_preprocessor import is_spacy_available
from utils.theme import inject_theme, hero, metric_tile, status_pill, pipeline, render_footer
from utils.chatbot import render_chatbot

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")


@st.cache_resource(show_spinner=False)
def bootstrap_app():
    """One-time setup: create DB tables and warm up the skill extractor."""
    init_db()
    extractor = get_skill_extractor(str(SKILLS_CSV))
    return extractor


def render_engine_status_sidebar():
    """Shows which semantic-similarity engine is active (required for transparency)."""
    from models.embeddings import get_embedding_engine

    with st.sidebar:
        st.markdown("### ⚙️ System Status")
        engine = get_embedding_engine()
        if engine.is_transformer_active():
            st.markdown(status_pill("Sentence Transformer", True), unsafe_allow_html=True)
            st.caption(f"`{engine.model_name}`")
        else:
            st.markdown(status_pill("TF-IDF Fallback", False), unsafe_allow_html=True)
            st.caption("Transformer model unavailable — using classic vectorization.")

        st.markdown("")
        if is_spacy_available():
            st.markdown(status_pill("spaCy NLP Engine", True), unsafe_allow_html=True)
        else:
            st.markdown(status_pill("Regex Fallback NLP", False), unsafe_allow_html=True)
            st.caption("spaCy model not found — core features still work.")

        st.markdown("---")
        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/9_AI_Intelligence_Center.py", label="🧠 AI Intelligence Center")


def workflow_card(col, emoji, title, desc, page_path):
    with col:
        st.markdown(
            f"""<div class="cai-card"><h4>{emoji} {title}</h4><p style="font-size:0.9rem;">{desc}</p></div>""",
            unsafe_allow_html=True,
        )
        st.page_link(page_path, label=f"Open {title} →")


def main():
    inject_theme()
    extractor = bootstrap_app()
    render_engine_status_sidebar()
    render_chatbot("home")

    hero(
        "CAREER<span style='color:#e0f2fe;'>AI</span>",
        "Your AI-Powered Career Intelligence Platform &mdash; analyze your resume, "
        "understand your skill gaps, practice interviews, and build your personalized "
        "career roadmap using transformer-based semantic embeddings.",
    )

    cta1, cta2, cta3, cta4 = st.columns(4)
    with cta1:
        st.page_link("pages/1_Resume_Analyzer.py", label="🚀 Analyze My Resume")
    with cta2:
        st.page_link("pages/2_Job_Matcher.py", label="🎯 Match a Job")
    with cta3:
        st.page_link("pages/9_AI_Intelligence_Center.py", label="🧠 Explore AI")
    with cta4:
        st.page_link("pages/4_Mock_Interview.py", label="🎤 Start Mock Interview")

    st.markdown("")
    st.info(
        "🎓 **Academic Prototype Notice:** This system is a final-year B.Tech "
        "Internship-II project. All scores (job match, skill gap, interview "
        "evaluation) are AI-assisted **academic assessment metrics** intended "
        "to support self-learning — they are **not** validated professional "
        "recruitment decisions."
    )

    st.markdown("### 📊 At a Glance")
    m1, m2, m3, m4 = st.columns(4)
    metric_tile(m1, str(len(extractor.all_skills)), "Skills in Dictionary")
    metric_tile(m2, "9", "Application Pages")
    metric_tile(m3, "8", "Core AI/NLP Modules")
    metric_tile(m4, "0", "Paid APIs Required")

    st.markdown("### 🧬 The AI Pipeline")
    st.caption("Every score you see on this platform is produced by this real, end-to-end pipeline — nothing is hard-coded.")
    pipeline([
        ("📄", "Resume"), ("🧠", "NLP"), ("🔍", "Skill Extraction"),
        ("🔢", "Embeddings"), ("📐", "Similarity"), ("🎯", "Matching"), ("🎤", "Interview AI"),
    ])

    st.markdown("###  ")
    st.markdown("### 🗂️ What can you do here?")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    workflow_card(r1c1, "📄", "Resume Analyzer", "Structured breakdown of skills, education, projects & certifications.", "pages/1_Resume_Analyzer.py")
    workflow_card(r1c2, "🎯", "Job Matcher", "Explainable AI Job Match Score: semantic similarity + skill overlap.", "pages/2_Job_Matcher.py")
    workflow_card(r1c3, "🧩", "Skill Gap Analysis", "Strong / Partial / Missing skills vs. your target job, with fixes.", "pages/3_Skill_Gap_Analysis.py")
    workflow_card(r1c4, "🎙️", "Mock Interview", "Tailored AI mock interview from your resume & target role.", "pages/4_Mock_Interview.py")

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    workflow_card(r2c1, "📊", "Interview Evaluation", "AI-assisted relevance, coverage & completeness scoring.", "pages/5_Interview_Evaluation.py")
    workflow_card(r2c2, "🗺️", "Career Roadmap", "Priority-ranked, week-by-week personalized learning plan.", "pages/6_Career_Roadmap.py")
    workflow_card(r2c3, "📈", "Dashboard", "All your results — match, gaps, interview — in one view.", "pages/7_Dashboard.py")
    workflow_card(r2c4, "🧠", "AI Intelligence Center", "See the AI engine status, pipeline & a live semantic-similarity demo.", "pages/9_AI_Intelligence_Center.py")

    st.markdown("---")
    st.subheader("Suggested Workflow")
    st.markdown(
        "`Resume Analyzer` → `Job Matcher` → `Skill Gap Analysis` → "
        "`Mock Interview` → `Interview Evaluation` → `Career Roadmap` → `Dashboard`"
    )
    st.caption(
        "Your session data (candidate name, analyses, interview results) is stored "
        "locally in a SQLite database (`database/careerai.db`) — nothing is sent to "
        "any external or paid AI service."
    )

    render_footer()


if __name__ == "__main__":
    main()
