"""
pages/4_Mock_Interview.py
============================
MODULE 5: AI Mock Interview — configuration, question generation, and
answer collection (text-based). Evaluation happens on submit and results
are shown in detail on the "Interview Evaluation" page.
"""

import streamlit as st

from config import APP_ICON, QUESTION_COUNT_OPTIONS, DIFFICULTY_OPTIONS, QUESTION_TYPE_OPTIONS
from database.database import create_interview_session, save_interview_answer, update_interview_session_summary
from interview.question_engine import get_question_engine
from interview.answer_evaluator import evaluate_answer
from interview.feedback import summarize_interview
from utils.session_state import init_session_state
from utils.validators import validate_answer_text
from utils.theme import (
    inject_theme, render_page_header, render_section_header,
    render_info_card, render_ai_badge, render_footer,
)
from utils.chatbot import render_chatbot

st.set_page_config(page_title="Mock Interview | CareerAI", page_icon=APP_ICON, layout="wide")
inject_theme()
init_session_state()
render_chatbot("mock_interview")

render_page_header("🎙️", "AI Mock Interview", "MODULE 5 — AI Interview Simulation",
                    "Questions are selected from a structured question bank based on your resume, projects, and target job.")
render_ai_badge("AI-ASSISTED EVALUATION")

resume_profile = st.session_state.get("resume_profile")
job_profile = st.session_state.get("job_profile")

if not resume_profile:
    render_info_card("Please analyze a resume first on the <b>Resume Analyzer</b> page.", variant="warning")
    st.stop()

render_section_header("Configure Your Interview", 1)
st.markdown('<div class="cai-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    num_questions = st.selectbox("Number of Questions", QUESTION_COUNT_OPTIONS, index=0)
with c2:
    difficulty = st.selectbox("Difficulty", DIFFICULTY_OPTIONS, index=3)
with c3:
    question_type = st.selectbox("Question Type", QUESTION_TYPE_OPTIONS, index=2)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")
if st.button("🎲 Generate Interview Questions", type="primary"):
    engine = get_question_engine()
    missing_skills = [
        g.skill for g in (st.session_state.get("skill_gap_items") or []) if g.status == "Missing"
    ]
    questions = engine.generate_questions(
        num_questions=num_questions,
        difficulty=difficulty,
        question_type=question_type,
        resume_skills=resume_profile["skills"],
        missing_skills=missing_skills,
        projects=resume_profile["projects"],
        job_role=job_profile["role"] if job_profile else "",
    )
    st.session_state["interview_questions"] = questions
    st.session_state["interview_answers"] = {}
    st.session_state["interview_results"] = None
    st.session_state["interview_summary"] = None

    if st.session_state.get("user_id"):
        session_id = create_interview_session(
            st.session_state["user_id"],
            job_profile["role"] if job_profile else "Not specified",
            num_questions,
            difficulty,
            question_type,
        )
        st.session_state["interview_session_id"] = session_id

questions = st.session_state.get("interview_questions")

if questions:
    render_section_header("Answer the Questions", 2)
    st.caption(
        "Type your answer in your own words. There is no time limit here — "
        "focus on being clear and specific."
    )

    for idx, q in enumerate(questions):
        st.markdown(
            f"""<div class="cai-card" style="margin-bottom:10px;">
            <span class="cai-pill cai-pill-on">Question {idx + 1} / {len(questions)}</span>
            &nbsp;&nbsp;<b>{q.category}</b> · {q.difficulty}
            <p style="margin-top:10px; font-size:1.02rem; color:#f5f7ff;">{q.question}</p>
            </div>""",
            unsafe_allow_html=True,
        )
        answer = st.text_area(
            f"Your answer to Q{idx + 1}",
            value=st.session_state["interview_answers"].get(idx, ""),
            key=f"answer_{idx}",
            height=120,
            label_visibility="collapsed",
        )
        st.session_state["interview_answers"][idx] = answer
        st.markdown("&nbsp;")

    st.markdown("---")
    if st.button("✅ Submit All Answers for Evaluation", type="primary"):
        unanswered = [
            i for i in range(len(questions))
            if validate_answer_text(st.session_state["interview_answers"].get(i, ""))
        ]
        if unanswered:
            st.warning(
                f"You left {len(unanswered)} question(s) unanswered "
                f"(Q{', Q'.join(str(i + 1) for i in unanswered)}). "
                "They will be scored as 0 — you can still submit, or go back and answer them."
            )

        with st.spinner("🧠 Evaluating your answers using NLP similarity scoring..."):
            results = []
            for idx, q in enumerate(questions):
                answer_text = st.session_state["interview_answers"].get(idx, "")
                evaluation = evaluate_answer(q.question, q.concepts, answer_text)
                evaluation.answer_text = answer_text  # attach for DB storage convenience
                results.append({"question": q, "evaluation": evaluation, "answer_text": answer_text})

                if st.session_state.get("interview_session_id"):
                    save_interview_answer(st.session_state["interview_session_id"], q, evaluation)

            summary = summarize_interview(results)

            if st.session_state.get("interview_session_id"):
                update_interview_session_summary(st.session_state["interview_session_id"], summary)

        st.session_state["interview_results"] = results
        st.session_state["interview_summary"] = summary
        st.success(f"✅ Interview evaluated! Overall score: {summary.overall_score}/10")
        render_info_card("➡️ Go to <b>Interview Evaluation</b> in the sidebar to see detailed feedback.", variant="success")
else:
    render_info_card("Configure your interview above and click <b>Generate Interview Questions</b> to begin.", variant="neutral")

render_footer()
