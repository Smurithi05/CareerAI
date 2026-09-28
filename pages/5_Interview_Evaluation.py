"""
pages/5_Interview_Evaluation.py
===================================
MODULE 6: Interview Answer Evaluation — detailed results display.
"""

import streamlit as st

from config import APP_ICON
from utils.session_state import init_session_state
from utils.helpers import score_label
from dashboard.charts import interview_performance_bar, technical_vs_hr_chart
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_metric_card, render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Interview Evaluation | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("interview_evaluation")

render_page_header("📊", "Interview Evaluation", "MODULE 6 — AI Answer Evaluation",
                    "AI-assisted evaluation of relevance, concept coverage, and completeness for each answer.")
render_ai_badge("AI-ASSISTED EVALUATION")

render_info_card(
    "⚠️ <b>Academic Disclaimer:</b> These scores are generated using NLP "
    "similarity and keyword-coverage techniques. They are an AI-assisted "
    "academic assessment and do not replace a real interview panel's "
    "judgement of tone, confidence, or deep domain expertise.",
    variant="warning",
)

results = st.session_state.get("interview_results")
summary = st.session_state.get("interview_summary")

if not results or not summary:
    render_info_card("Complete a mock interview on the <b>Mock Interview</b> page first.", variant="neutral")
    st.stop()

render_section_header("Overall Performance", 1)
c1, c2, c3 = st.columns(3)
render_metric_card(c1, f"{summary.overall_score}/10", f"Overall Score ({score_label(summary.overall_score)})")
render_metric_card(c2, str(summary.total_questions), "Questions Answered")
render_metric_card(c3, ", ".join(summary.weak_categories) if summary.weak_categories else "None", "Weakest Categories")

st.markdown("")
render_info_card(summary.overall_feedback, variant="neutral")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(interview_performance_bar(summary.category_scores), use_container_width=True)
with col2:
    st.plotly_chart(technical_vs_hr_chart(summary.category_scores), use_container_width=True)

if summary.weak_concepts:
    st.markdown('<div class="cai-card">', unsafe_allow_html=True)
    st.markdown("**Concepts most frequently missed across your answers:**")
    st.write(", ".join(summary.weak_concepts))
    st.markdown('</div>', unsafe_allow_html=True)

render_section_header("Question-by-Question Breakdown", 2)

for idx, r in enumerate(results):
    q = r["question"]
    ev = r["evaluation"]
    with st.expander(f"Q{idx + 1}. [{q.category} · {q.difficulty}] — Overall: {ev.overall_score}/10 ({score_label(ev.overall_score)})"):
        st.markdown(f"**Question:** {q.question}")
        st.markdown(f"**Your Answer:** {r['answer_text'] or '_No answer provided_'}")

        m1, m2, m3 = st.columns(3)
        render_metric_card(m1, f"{ev.relevance_score}/10", "Semantic Relevance")
        render_metric_card(m2, f"{ev.concept_coverage_score}/10", "Concept Coverage")
        render_metric_card(m3, f"{ev.completeness_score}/10", "Completeness")

        st.markdown("**✅ What you did well:**")
        for s in ev.strengths:
            st.markdown(f"- {s}")

        st.markdown("**🔧 How to improve:**")
        for imp in ev.improvements:
            st.markdown(f"- {imp}")

        if ev.missing_concepts:
            st.markdown(f"**Concepts to mention next time:** {', '.join(ev.missing_concepts)}")

render_info_card("➡️ Next step: view your <b>Career Roadmap</b>, built using these interview results plus your skill gaps.", variant="success")
render_footer()
