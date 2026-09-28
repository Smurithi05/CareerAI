"""
pages/6_Career_Roadmap.py
=============================
MODULE 7: Personalized Career Roadmap UI.
"""

import streamlit as st

from config import APP_ICON
from database.database import save_roadmap
from roadmap.roadmap_generator import generate_roadmap
from utils.session_state import init_session_state
from dashboard.charts import roadmap_progress_chart
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Career Roadmap | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("roadmap")

render_page_header("🗺️", "Personalized Career Roadmap", "MODULE 7 — Priority-Ranked Learning Plan",
                    "A week-by-week learning plan built from your skill gaps and interview weaknesses.")
render_ai_badge("RULE-BASED PLANNING")

skill_gap_items = st.session_state.get("skill_gap_items")
if not skill_gap_items:
    render_info_card("Please complete <b>Skill Gap Analysis</b> first.", variant="warning")
    st.stop()

summary = st.session_state.get("interview_summary")
weak_concepts = summary.weak_concepts if summary else []

render_section_header("Plan Settings", 1)
num_weeks = st.slider("Number of weeks to plan for", min_value=2, max_value=8, value=4)

if st.button("🧭 Generate Roadmap", type="primary"):
    roadmap = generate_roadmap(skill_gap_items, weak_concepts, num_weeks=num_weeks)
    st.session_state["roadmap"] = roadmap
    if st.session_state.get("user_id"):
        save_roadmap(st.session_state["user_id"], roadmap)
    st.success("✅ Roadmap generated.")

roadmap = st.session_state.get("roadmap")

if roadmap:
    render_section_header("Week-by-Week Plan", 2)
    st.plotly_chart(roadmap_progress_chart(roadmap["weekly_plan"]), use_container_width=True)

    cols = st.columns(len(roadmap["weekly_plan"]))
    for col, week in zip(cols, roadmap["weekly_plan"]):
        with col:
            topics_html = "".join(f"<li>{t}</li>" for t in week["topics"])
            st.markdown(
                f"""<div class="cai-card">
                <h4>📅 Week {week['week']}</h4>
                <ul style="padding-left:18px; font-size:0.88rem;">{topics_html}</ul>
                </div>""",
                unsafe_allow_html=True,
            )

    render_section_header("Priority-Ranked Skill Recommendations", 3)
    st.caption(
        "Priority = (Job Importance × Gap Severity) + Interview Weakness Bonus — "
        "a transparent rule-based prioritization, not a black-box ML ranking."
    )

    for item in roadmap["prioritized_skills"]:
        with st.expander(f"🔹 {item['skill']}  ·  Priority Score: {item['priority_score']}"):
            st.markdown(f"**Why prioritized:** {item['reason']}")
            st.markdown(f"**Recommendation:** {item['recommendation']}")

    if not roadmap["prioritized_skills"]:
        render_info_card("No significant skill gaps found — your roadmap focuses on interview practice and project polish!", variant="success")

    render_info_card("➡️ View everything together on the <b>Dashboard</b> page.", variant="success")
else:
    render_info_card("Click <b>Generate Roadmap</b> above to build your personalized plan.", variant="neutral")

render_footer()
