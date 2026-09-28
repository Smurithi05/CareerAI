"""
pages/8_About.py
====================
About page — required academic disclosures, architecture summary, and a
clear breakdown of AI/ML vs rule-based vs scoring-logic components.
"""

import streamlit as st

from config import APP_ICON
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="About | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
render_chatbot("about")

render_page_header("ℹ️", "About CareerAI", "Project Overview",
                    "AI-Powered Career Intelligence and Mock Interview Assessment System")
render_ai_badge("ACADEMIC PROJECT")

st.markdown(
    """<div class="cai-card">
    <b>CareerAI — AI-Powered Career Intelligence and Mock Interview Assessment System</b>
    <p>This is a final-year B.Tech Information Technology Internship-II academic
    project. It demonstrates practical, end-to-end application of Natural
    Language Processing, semantic similarity, rule-based recommendation logic,
    document processing, database management, and interactive data
    visualization — built entirely with free and open-source tools.</p>
    </div>""",
    unsafe_allow_html=True,
)

render_info_card(
    "🎓 <b>This system is an academic prototype.</b> The generated scores are "
    "intended to support self-assessment and learning, and should <b>not</b> be "
    "treated as professional recruitment decisions.",
    variant="warning",
)

render_section_header("What is actually AI/ML here — and what isn't", 1)
st.markdown(
    "A common mistake in student AI projects is labeling every component as "
    "\"Machine Learning\". This project is explicit about the distinction:"
)

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """<div class="cai-card">
        <h4>🤖 AI / Pre-trained ML Model</h4>
        <ul>
        <li><b>Semantic similarity</b> via <code>sentence-transformers</code>
        (<code>all-MiniLM-L6-v2</code>), a pre-trained transformer embedding model.</li>
        <li>Cosine similarity over dense embeddings to measure meaning-level
        closeness between resume, JD, and interview-answer text.</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        """<div class="cai-card">
        <h4>🧠 Classical NLP (rule/statistics based)</h4>
        <ul>
        <li>spaCy-based sentence segmentation & lemmatization (with a
        regex-based fallback if spaCy's model is unavailable).</li>
        <li>TF-IDF vectorization (used as the fallback similarity engine).</li>
        <li>Regex/keyword-based section splitting, contact-info extraction,
        and skill-dictionary matching (exact, alias, and fuzzy).</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """<div class="cai-card">
        <h4>📐 Rule-Based Scoring Logic</h4>
        <ul>
        <li>The <b>Final Match Score</b> formula
        (<code>0.6 × semantic + 0.4 × skill overlap</code>) is a manually designed,
        documented heuristic — not a trained/learned weighting.</li>
        <li>Skill Strong/Partial/Missing thresholds are fixed cutoffs on
        cosine similarity, chosen for interpretability.</li>
        <li>Interview answer scoring combines three explicit sub-scores with
        fixed weights.</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        """<div class="cai-card">
        <h4>🗂️ Recommendation / Planning Logic</h4>
        <ul>
        <li>Skill-gap learning recommendations come from a curated knowledge
        base (<code>models/scoring.py</code>), with a generic template as fallback.</li>
        <li>The weekly roadmap uses a rule-based priority score
        (importance × gap severity + interview-weakness bonus) to order
        and schedule topics — a scheduling/prioritization algorithm, not
        an ML model.</li>
        </ul>
        </div>""",
        unsafe_allow_html=True,
    )

render_section_header("System Architecture", 2)
st.code(
    """
USER
 └── Streamlit Web Application
       ├── Resume Processing ──► Text Extraction ──┐
       └── Job Description Processing ──► Preprocessing ──┤
                                                            ▼
                                                       NLP Engine
                                    ┌───────────────┬───────────────┐
                             Resume Skill      Job Skill        Semantic
                             Extraction        Extraction       Similarity
                                    └───────────────┴───────────────┘
                                                    ▼
                                              Job Matching
                                                    ▼
                                           Skill Gap Analysis
                                                    ▼
                                       Interview Question Engine
                                                    ▼
                                       Interview Answer Analysis
                                                    ▼
                                        Performance Analysis
                                                    ▼
                                  Personalized Learning Roadmap
                                                    ▼
                                            AI Dashboard
                                                    ▼
                                             SQLite Database
    """,
    language="text",
)

render_section_header("Technology Stack", 3)
t1, t2, t3, t4 = st.columns(4)
for col, emoji, title, body in [
    (t1, "🖥️", "UI", "Streamlit"),
    (t2, "🧠", "NLP", "spaCy + regex fallback"),
    (t3, "🔢", "Semantic AI", "sentence-transformers (MiniLM-L6-v2) + TF-IDF fallback"),
    (t4, "📄", "Documents", "pypdf, python-docx"),
]:
    with col:
        st.markdown(f'<div class="cai-card"><h4>{emoji} {title}</h4><p style="font-size:0.85rem;">{body}</p></div>', unsafe_allow_html=True)

st.markdown("")
t5, t6, t7 = st.columns(3)
for col, emoji, title, body in [
    (t5, "📊", "Visualization", "Plotly"),
    (t6, "🗄️", "Database", "SQLite (via sqlite3)"),
    (t7, "🧪", "Testing", "pytest"),
]:
    with col:
        st.markdown(f'<div class="cai-card"><h4>{emoji} {title}</h4><p style="font-size:0.85rem;">{body}</p></div>', unsafe_allow_html=True)

render_section_header("Privacy & Data Handling", 4)
st.markdown(
    """<div class="cai-card">
    <ul>
    <li>Resumes are processed <b>entirely locally</b> on this machine — no file
    content is uploaded to any external or paid AI API.</li>
    <li>No paid API key is required or used anywhere in this application.</li>
    <li>Session results are stored <b>locally</b> in a SQLite database
    (<code>database/careerai.db</code>) for later reference; uploaded resume files
    themselves are held only in memory for the duration of the analysis
    and are not permanently saved to disk.</li>
    </ul>
    </div>""",
    unsafe_allow_html=True,
)

render_section_header("Known Limitations", 5)
st.markdown(
    """<div class="cai-card">
    <ul>
    <li>Section detection and field extraction are heuristic; unusual resume
    formats (heavy graphics, multi-column PDFs, scanned images without a
    text layer) may parse less accurately.</li>
    <li>The skill dictionary, while extensible, cannot cover every possible
    technology; unseen skills may be missed unless added to
    <code>data/skills.csv</code>.</li>
    <li>Interview answer scoring evaluates textual relevance/coverage/
    completeness only — it cannot assess spoken delivery, confidence, or
    true depth of understanding the way a human interviewer can.</li>
    <li>No real-world accuracy/precision/recall figures are claimed anywhere
    in this project, since no labeled evaluation dataset was collected;
    any such measurement would need to be run explicitly using the test
    suite in <code>tests/</code> against real annotated data.</li>
    </ul>
    </div>""",
    unsafe_allow_html=True,
)

render_section_header("Future Scope", 6)
st.markdown(
    """<div class="cai-card">
    <ul>
    <li>Multilingual resume and interview support.</li>
    <li>Real-time voice-based mock interviews (speech-to-text integration).</li>
    <li>Larger, ontology-based skill graph (e.g. skill-to-skill relationships).</li>
    <li>Cloud deployment with user authentication and a recruiter-facing view.</li>
    <li>Domain-specific fine-tuned models for stronger semantic matching.</li>
    <li>Facial/emotion analysis for interview delivery feedback — <b>only</b>
    with explicit consent and clear ethical safeguards, if ever added.</li>
    </ul>
    </div>""",
    unsafe_allow_html=True,
)

render_footer()
