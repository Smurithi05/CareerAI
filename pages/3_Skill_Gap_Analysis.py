"""
pages/3_Skill_Gap_Analysis.py
=================================
MODULE 4: Skill Gap Analysis UI — Strong / Partial / Missing classification
with per-skill importance and learning recommendations.
"""

import streamlit as st
import pandas as pd

from config import APP_ICON
from models.scoring import classify_skill_gaps, get_recommendation
from utils.session_state import init_session_state
from dashboard.charts import skill_match_bar_chart, skill_gap_pie_chart
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Skill Gap Analysis | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("skill_gap")

render_page_header("🧩", "Skill Gap Analysis", "MODULE 4 — Skill Gap Classification",
                    "Strong Match / Partial Match / Missing skills vs. your target job, with recommendations.")
render_ai_badge("AI + RULE-BASED")

resume_profile = st.session_state.get("resume_profile")
job_profile = st.session_state.get("job_profile")

if not resume_profile or not job_profile:
    render_info_card("Please complete both the <b>Resume Analyzer</b> and <b>Job Matcher</b> pages first.", variant="warning")
    st.stop()

gap_items = classify_skill_gaps(
    resume_profile["skills"],
    job_profile["required_skills"],
    job_profile["preferred_skills"],
)
st.session_state["skill_gap_items"] = gap_items

strong = [g for g in gap_items if g.status == "Strong Match"]
partial = [g for g in gap_items if g.status == "Partial Match"]
missing = [g for g in gap_items if g.status == "Missing"]

render_section_header("Overview", 1)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(skill_match_bar_chart(len(strong), len(partial), len(missing)), use_container_width=True)
with col2:
    st.plotly_chart(skill_gap_pie_chart(len(strong), len(partial), len(missing)), use_container_width=True)

render_section_header("Detailed Breakdown", 2)
tab1, tab2, tab3 = st.tabs([f"✅ Strong Match ({len(strong)})", f"🟡 Partial Match ({len(partial)})", f"❌ Missing ({len(missing)})"])

with tab1:
    if strong:
        df = pd.DataFrame(
            [{"Skill": g.skill, "Importance": g.importance, "Matched Resume Skill": g.matched_resume_skill} for g in strong]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        render_info_card("No strong matches found yet.", variant="neutral")

with tab2:
    if partial:
        for g in partial:
            with st.expander(f"🟡 {g.skill}  ·  Importance: {g.importance}  ·  Similarity: {g.similarity_score:.2f}"):
                st.markdown(f"**Closest resume skill:** {g.matched_resume_skill or 'N/A'}")
                st.markdown(f"**Recommended Learning Topic:** {get_recommendation(g.skill)}")
    else:
        render_info_card("No partial matches found.", variant="neutral")

with tab3:
    if missing:
        for g in missing:
            with st.expander(f"❌ {g.skill}  ·  Priority: {g.importance}"):
                st.markdown(f"**Status:** Missing &nbsp;·&nbsp; **Importance:** {g.importance}")
                st.markdown(f"**Recommended Learning Topic & Mini-Project:** {get_recommendation(g.skill)}")
    else:
        render_info_card("No missing skills — great alignment with this job description!", variant="success")

render_info_card("➡️ Next step: take an AI-generated <b>Mock Interview</b> tailored to your resume and this job role.", variant="success")
render_footer()
