"""
pages/2_Job_Matcher.py
=========================
MODULE 2 (Job Description Intelligence) + MODULE 3 (AI Job Matching) UI.
"""

import os
import streamlit as st

from config import SKILLS_CSV, SAMPLE_JD_DIR, APP_ICON, SEMANTIC_WEIGHT, SKILL_OVERLAP_WEIGHT
from database.database import save_job_analysis, save_skill_analysis
from nlp.job_parser import parse_job_description, JobDescriptionParsingError
from nlp.skill_extractor import get_skill_extractor
from models.scoring import compute_job_match
from utils.validators import validate_job_description
from utils.session_state import init_session_state
from utils.helpers import pct, format_skill_list
from dashboard.charts import gauge_chart, job_match_radar_chart
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_metric_card, render_info_card, render_ai_badge, render_footer, skill_chips,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Job Matcher | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("job_matcher")

render_page_header("🎯", "Job Matcher", "MODULE 2 & 3 — Job Intelligence + AI Job Matching",
                    "Paste a target job description and get an explainable AI match score.")
render_ai_badge("SEMANTIC ANALYSIS")

if not st.session_state.get("resume_profile"):
    render_info_card("Please analyze a resume first on the <b>Resume Analyzer</b> page.", variant="warning")
    st.stop()

with st.expander("ℹ️ How the Final Match Score is calculated (click to expand)"):
    st.markdown(
        f"""
        This is a **transparent, explainable academic scoring formula** —
        not a scientifically validated hiring/recruitment score.

        ```
        Final Match Score = {SEMANTIC_WEIGHT} * Semantic Similarity
                           + {SKILL_OVERLAP_WEIGHT} * Skill Overlap Score
        ```

        - **Semantic Similarity**: cosine similarity between embeddings of
          your full resume text and the full job description text (using
          Sentence-Transformers, or a TF-IDF fallback if the transformer
          model is unavailable).
        - **Skill Overlap Score**: fraction of the job's required/preferred
          skills that are explicitly present in your resume's skill list.
        """
    )

render_section_header("Provide a Job Description", 1)

sample_files = sorted(os.listdir(SAMPLE_JD_DIR)) if SAMPLE_JD_DIR.exists() else []
sample_labels = ["-- None (paste your own) --"] + [f.replace("_", " ").replace(".txt", "").title() for f in sample_files]
choice = st.selectbox("Or load a sample job description:", sample_labels)

default_text = ""
if choice != sample_labels[0]:
    idx = sample_labels.index(choice) - 1
    with open(SAMPLE_JD_DIR / sample_files[idx], "r", encoding="utf-8") as f:
        default_text = f.read()

jd_text = st.text_area("Job Description Text", value=default_text, height=280)

if st.button("🔍 Analyze Match", type="primary"):
    error = validate_job_description(jd_text)
    if error:
        st.error(error)
    else:
        try:
            with st.spinner("🧠 Parsing job description and computing semantic job match..."):
                extractor = get_skill_extractor(str(SKILLS_CSV))
                job_profile = parse_job_description(jd_text, extractor)
                resume_profile = st.session_state["resume_profile"]
                match_result = compute_job_match(resume_profile, job_profile)

            st.session_state["job_profile"] = job_profile
            st.session_state["match_result"] = match_result

            if st.session_state.get("user_id"):
                job_analysis_id = save_job_analysis(st.session_state["user_id"], job_profile)
                st.session_state["job_analysis_id"] = job_analysis_id
                save_skill_analysis(
                    st.session_state["user_id"],
                    st.session_state.get("resume_analysis_id"),
                    job_analysis_id,
                    match_result,
                )
            st.success("✅ Job match analysis complete.")
        except JobDescriptionParsingError as e:
            st.error(f"⚠️ {e}")
        except Exception:
            st.error("⚠️ Something went wrong while analyzing this job description. Please check the text and try again.")

job_profile = st.session_state.get("job_profile")
match_result = st.session_state.get("match_result")

if job_profile and match_result:
    render_section_header("AI Match Results", 2)
    st.caption(f"Semantic Engine used: **{match_result.engine_name}**")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(gauge_chart(pct(match_result.final_score), "Overall Job Match (%)"), use_container_width=True)
    with col2:
        st.plotly_chart(
            job_match_radar_chart(
                pct(match_result.semantic_similarity),
                pct(match_result.skill_overlap_score),
                pct(match_result.resume_skill_coverage),
            ),
            use_container_width=True,
        )

    m1, m2, m3, m4 = st.columns(4)
    render_metric_card(m1, f"{pct(match_result.final_score)}%", "Overall Job Match")
    render_metric_card(m2, f"{pct(match_result.semantic_similarity)}%", "Semantic Similarity")
    render_metric_card(m3, f"{pct(match_result.skill_overlap_score)}%", "Skill Overlap")
    render_metric_card(m4, f"{pct(match_result.resume_skill_coverage)}%", "Resume Skill Coverage")

    render_section_header("Job Profile Extracted", 3)
    jc1, jc2 = st.columns(2)
    with jc1:
        st.markdown('<div class="cai-card">', unsafe_allow_html=True)
        st.markdown(f"**Detected Role:** {job_profile['role']}")
        st.markdown("**Required Skills:**")
        skill_chips(job_profile['required_skills'], variant="matched")
        st.markdown("**Preferred Skills:**")
        skill_chips(job_profile['preferred_skills'], variant="matched")
        st.markdown('</div>', unsafe_allow_html=True)
    with jc2:
        st.markdown('<div class="cai-card">', unsafe_allow_html=True)
        st.markdown("**Tools Mentioned:**")
        skill_chips(job_profile['tools'], variant="matched")
        st.markdown(f"**Experience Requirement(s):** {', '.join(job_profile['experience']) or 'Not specified'}")
        st.markdown(f"**Education Requirement(s):** {', '.join(job_profile['education_requirements']) or 'Not specified'}")
        st.markdown('</div>', unsafe_allow_html=True)

    render_section_header("Matched / Missing Skills", 4)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="cai-card">', unsafe_allow_html=True)
        st.markdown("#### ✅ Matched Skills")
        skill_chips(match_result.matched_skills, variant="matched")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="cai-card">', unsafe_allow_html=True)
        st.markdown("#### 🟡 Partial Matches")
        if match_result.partial_skills:
            for p in match_result.partial_skills:
                st.write(f"- {p['skill']} (≈ {p['matched_resume_skill']}, similarity {p['score']:.2f})")
        else:
            st.write("None")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="cai-card">', unsafe_allow_html=True)
        st.markdown("#### ❌ Missing Skills")
        skill_chips(match_result.missing_skills, variant="missing")
        st.markdown('</div>', unsafe_allow_html=True)

    render_info_card("➡️ Next step: go to <b>Skill Gap Analysis</b> in the sidebar for detailed recommendations.", variant="success")
else:
    render_info_card("Provide a job description above and click <b>Analyze Match</b> to see results.", variant="neutral")

render_footer()
