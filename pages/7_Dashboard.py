"""
pages/7_Dashboard.py
========================
MODULE 8: AI Career Dashboard — a single consolidated view of resume
analysis, job matching, skill gaps, and interview performance.
"""

import streamlit as st

from config import APP_ICON
from utils.session_state import init_session_state
from utils.helpers import pct, score_label
from dashboard.charts import (
    gauge_chart,
    skill_match_bar_chart,
    skill_gap_pie_chart,
    interview_performance_bar,
    technical_vs_hr_chart,
    roadmap_progress_chart,
)
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_metric_card, render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Dashboard | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("dashboard")

render_page_header("📈", "AI Career Dashboard", "MODULE 8 — Consolidated Analytics",
                    "A single consolidated view of every analysis performed in this session.")
render_ai_badge("AI INSIGHTS")

resume_profile = st.session_state.get("resume_profile")
job_profile = st.session_state.get("job_profile")
match_result = st.session_state.get("match_result")
skill_gap_items = st.session_state.get("skill_gap_items")
interview_summary = st.session_state.get("interview_summary")
roadmap = st.session_state.get("roadmap")

if not resume_profile:
    render_info_card("No data yet — start with the <b>Resume Analyzer</b> page.", variant="warning")
    st.stop()

render_section_header("Candidate Overview", 1)
c1, c2, c3, c4 = st.columns(4)
render_metric_card(c1, resume_profile["name"], "Candidate Name")
render_metric_card(c2, job_profile["role"] if job_profile else "Not set", "Target Role")
render_metric_card(c3, str(len(resume_profile["skills"])), "Resume Skills Detected")
render_metric_card(c4, f"{interview_summary.overall_score}/10" if interview_summary else "Not taken yet", "Interview Score")

render_section_header("Job Match Summary", 2)
if match_result:
    m1, m2, m3, m4 = st.columns(4)
    render_metric_card(m1, f"{pct(match_result.final_score)}%", "Overall Job Match")
    render_metric_card(m2, f"{pct(match_result.semantic_similarity)}%", "Semantic Similarity")
    render_metric_card(m3, f"{pct(match_result.skill_overlap_score)}%", "Skill Overlap")
    render_metric_card(m4, f"{pct(match_result.resume_skill_coverage)}%", "Resume Skill Coverage")
    st.plotly_chart(gauge_chart(pct(match_result.final_score), "Overall Job Match (%)"), use_container_width=True)
else:
    render_info_card("Run <b>Job Matcher</b> to see your job match score here.", variant="neutral")

render_section_header("Skill Gap Overview", 3)
if skill_gap_items:
    strong = len([g for g in skill_gap_items if g.status == "Strong Match"])
    partial = len([g for g in skill_gap_items if g.status == "Partial Match"])
    missing = len([g for g in skill_gap_items if g.status == "Missing"])

    cc1, cc2 = st.columns(2)
    with cc1:
        st.plotly_chart(skill_match_bar_chart(strong, partial, missing), use_container_width=True)
    with cc2:
        st.plotly_chart(skill_gap_pie_chart(strong, partial, missing), use_container_width=True)
else:
    render_info_card("Run <b>Skill Gap Analysis</b> to see your skill breakdown here.", variant="neutral")

render_section_header("Interview Performance", 4)
if interview_summary:
    ic1, ic2 = st.columns(2)
    with ic1:
        st.plotly_chart(interview_performance_bar(interview_summary.category_scores), use_container_width=True)
    with ic2:
        st.plotly_chart(technical_vs_hr_chart(interview_summary.category_scores), use_container_width=True)
    mc, _ = st.columns([1, 3])
    render_metric_card(mc, f"{interview_summary.overall_score}/10", f"Overall ({score_label(interview_summary.overall_score)})")
else:
    render_info_card("Take the <b>Mock Interview</b> to see your interview performance here.", variant="neutral")

render_section_header("Learning Roadmap Progress", 5)
if roadmap:
    st.plotly_chart(roadmap_progress_chart(roadmap["weekly_plan"]), use_container_width=True)
    st.caption(f"{len(roadmap['prioritized_skills'])} prioritized skills scheduled across {len(roadmap['weekly_plan'])} week(s).")
else:
    render_info_card("Generate your <b>Career Roadmap</b> to see progress tracking here.", variant="neutral")

render_footer()
