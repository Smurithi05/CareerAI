"""
utils/chatbot.py
===================
A small, dynamic "🤖 Ask CareerAI" assistant.

This is NOT a static FAQ. It inspects the same shared `st.session_state`
every module already reads/writes (resume_profile, job_profile,
match_result, skill_gap_items, interview_results/summary, roadmap) plus
which page it is being shown on, and composes its answer from that live
data — so the same question ("what should I do next?") gives a different,
personalized answer depending on how far a given user has actually
progressed through the pipeline.

Consistent with the rest of the project ("No paid APIs. All data stored
locally."), this uses no external AI API — it's a lightweight rule +
keyword based response engine, the same spirit as CareerAI's other
rule-based modules (skill gap classification, roadmap generation).

Usage: call `render_chatbot(page_key)` once on a page (see PAGE_INFO for
valid keys). It renders itself in the sidebar so it never disturbs a
page's existing layout.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Static knowledge about each module: what it does + where it naturally
# leads next in the suggested workflow. Used to answer "what is X" / "what
# do I do on this page" questions and to recommend a next step.
# ---------------------------------------------------------------------------
PAGE_INFO = {
    "home": {
        "label": "Home",
        "path": "app.py",
        "desc": "the landing page — an overview of the whole pipeline with quick links into every module.",
        "next": "resume_analyzer",
    },
    "resume_analyzer": {
        "label": "Resume Analyzer",
        "path": "pages/1_Resume_Analyzer.py",
        "desc": "MODULE 1 — upload your resume (PDF/DOCX) and CareerAI extracts your skills, education, projects and certifications.",
        "next": "job_matcher",
    },
    "job_matcher": {
        "label": "Job Matcher",
        "path": "pages/2_Job_Matcher.py",
        "desc": "MODULE 2 & 3 — paste a target job description and get an explainable AI Job Match Score (semantic similarity + skill overlap).",
        "next": "skill_gap",
    },
    "skill_gap": {
        "label": "Skill Gap Analysis",
        "path": "pages/3_Skill_Gap_Analysis.py",
        "desc": "MODULE 4 — classifies each job skill as Strong Match / Partial Match / Missing, with learning recommendations.",
        "next": "mock_interview",
    },
    "mock_interview": {
        "label": "Mock Interview",
        "path": "pages/4_Mock_Interview.py",
        "desc": "MODULE 5 — generates interview questions from your resume, projects and target role, and collects your written answers.",
        "next": "interview_evaluation",
    },
    "interview_evaluation": {
        "label": "Interview Evaluation",
        "path": "pages/5_Interview_Evaluation.py",
        "desc": "MODULE 6 — AI-assisted scoring of your interview answers (relevance, concept coverage, completeness) with per-question feedback.",
        "next": "roadmap",
    },
    "roadmap": {
        "label": "Career Roadmap",
        "path": "pages/6_Career_Roadmap.py",
        "desc": "MODULE 7 — a priority-ranked, week-by-week learning plan built from your skill gaps and interview weak areas.",
        "next": "dashboard",
    },
    "dashboard": {
        "label": "Dashboard",
        "path": "pages/7_Dashboard.py",
        "desc": "MODULE 8 — a single consolidated view of your resume, job match, skill gaps, and interview performance.",
        "next": "about",
    },
    "about": {
        "label": "About",
        "path": "pages/8_About.py",
        "desc": "the project overview, academic disclosures, and a breakdown of what's real AI vs. rule-based logic.",
        "next": None,
    },
    "ai_center": {
        "label": "AI Intelligence Center",
        "path": "pages/9_AI_Intelligence_Center.py",
        "desc": "shows which NLP/semantic engines are actually active right now, the end-to-end AI pipeline, and a live semantic-similarity demo.",
        "next": None,
    },
}

_TOPIC_KEYWORDS = {
    "resume_analyzer": ["resume", "cv", "upload resume"],
    "job_matcher": ["job matcher", "job match", "job description", " jd", "match score"],
    "skill_gap": ["skill gap", "missing skill", "gap analysis", "strong match", "partial match"],
    "mock_interview": ["mock interview", "interview question", "practice interview"],
    "interview_evaluation": ["interview evaluation", "interview score", "interview feedback", "evaluate my answer"],
    "roadmap": ["roadmap", "learning plan", "week by week", "what should i learn"],
    "dashboard": ["dashboard", "all my results", "everything in one"],
    "about": ["about this project", "academic project", "what is this project"],
    "ai_center": ["ai engine", "embedding", "transformer", "spacy", "which ai", "ai intelligence"],
}


def _find_topic(low_text: str):
    for key, kws in _TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in low_text:
                return key
    return None


def _session_snapshot():
    """Read the same shared session_state keys every page already reads/writes."""
    return {
        "resume_profile": st.session_state.get("resume_profile"),
        "job_profile": st.session_state.get("job_profile"),
        "match_result": st.session_state.get("match_result"),
        "skill_gap_items": st.session_state.get("skill_gap_items"),
        "interview_questions": st.session_state.get("interview_questions"),
        "interview_summary": st.session_state.get("interview_summary"),
        "roadmap": st.session_state.get("roadmap"),
    }


def _progress_lines(snap):
    """Human-readable lines describing what's actually in THIS session right now."""
    lines = []

    rp = snap["resume_profile"]
    if rp:
        n_skills = len(rp.get("skills", []) or [])
        lines.append(f"✅ Resume analyzed for **{rp.get('name', 'you')}** — {n_skills} skill(s) detected.")
    else:
        lines.append("⬜ No resume analyzed yet.")

    jp = snap["job_profile"]
    lines.append(f"✅ Target job set: **{jp.get('role') or 'a job description'}**." if jp else "⬜ No target job description added yet.")

    mr = snap["match_result"]
    if mr:
        lines.append(f"✅ Job Match Score: **{round(mr.final_score * 100)}%**.")

    sg = snap["skill_gap_items"]
    if sg:
        missing = [g.skill for g in sg if g.status == "Missing"]
        tail = f": {', '.join(missing[:5])}{'…' if len(missing) > 5 else ''}." if missing else " (none missing)."
        lines.append(f"✅ Skill Gap Analysis done — {len(missing)} missing skill(s){tail}")

    iq = snap["interview_questions"]
    isum = snap["interview_summary"]
    if isum:
        lines.append(f"✅ Mock interview evaluated — overall score **{isum.overall_score}/10**.")
        if isum.weak_categories:
            lines.append(f"   Weakest area(s): {', '.join(isum.weak_categories[:3])}.")
    elif iq:
        lines.append(f"🟡 {len(iq)} interview question(s) generated, not yet submitted for evaluation.")

    rm = snap["roadmap"]
    if rm:
        lines.append(f"✅ Career roadmap generated ({len(rm)} week(s)).")

    return lines


def _next_recommended_key(snap):
    if not snap["resume_profile"]:
        return "resume_analyzer"
    if not snap["job_profile"]:
        return "job_matcher"
    if not snap["skill_gap_items"]:
        return "skill_gap"
    if not snap["interview_summary"]:
        return "mock_interview"
    if not snap["roadmap"]:
        return "roadmap"
    return "dashboard"


def _answer(user_text: str, page_key: str) -> str:
    low = user_text.strip().lower()
    snap = _session_snapshot()
    here = PAGE_INFO.get(page_key, PAGE_INFO["home"])

    # "where am I / what does this page do"
    if any(p in low for p in ["what is this page", "what does this page", "where am i",
                               "what can i do here", "help me here", "explain this page"]):
        msg = f"You're on **{here['label']}** — {here['desc']}"
        nxt = here.get("next")
        if nxt:
            msg += f"\n\nWhen you're done here, the natural next step is **{PAGE_INFO[nxt]['label']}** (`{PAGE_INFO[nxt]['path']}`)."
        return msg

    # "what should I do next"
    if any(p in low for p in ["what next", "next step", "what should i do", "what now", "where should i go"]):
        lines = _progress_lines(snap)
        nxt = PAGE_INFO[_next_recommended_key(snap)]
        return ("Here's where your session stands:\n\n" + "\n".join(f"- {l}" for l in lines) +
                f"\n\n**Suggested next step:** open **{nxt['label']}** (`{nxt['path']}`) — {nxt['desc']}")

    # "progress / status / summary"
    if any(p in low for p in ["progress", "status", "summarize my", "where do i stand", "my session"]):
        lines = _progress_lines(snap)
        return "Here's your current CareerAI session:\n\n" + "\n".join(f"- {l}" for l in lines)

    # topic-specific: explain a module + weave in live data if it exists
    topic = _find_topic(low)
    if topic:
        info = PAGE_INFO[topic]
        reply = f"**{info['label']}** — {info['desc']}"
        if topic == "resume_analyzer" and snap["resume_profile"]:
            rp = snap["resume_profile"]
            reply += (f"\n\nYou've already analyzed a resume — {len(rp.get('skills', []) or [])} skill(s) "
                      f"detected, {len(rp.get('projects', []) or [])} project(s) found.")
        elif topic == "job_matcher" and snap["match_result"]:
            reply += f"\n\nYour current match score is **{round(snap['match_result'].final_score * 100)}%**."
        elif topic == "skill_gap" and snap["skill_gap_items"]:
            missing = [g.skill for g in snap["skill_gap_items"] if g.status == "Missing"]
            reply += f"\n\nYou currently have {len(missing)} missing skill(s)" + (f": {', '.join(missing[:6])}." if missing else ".")
        elif topic in ("mock_interview", "interview_evaluation") and snap["interview_summary"]:
            isum = snap["interview_summary"]
            reply += f"\n\nYour last mock interview scored **{isum.overall_score}/10**."
            if isum.weak_categories:
                reply += f" Weakest area(s): {', '.join(isum.weak_categories[:3])}."
        elif topic == "roadmap" and snap["roadmap"]:
            reply += f"\n\nYou already have a {len(snap['roadmap'])}-week roadmap generated."
        reply += f"\n\nOpen it: `{info['path']}`."
        return reply

    # short greeting
    if len(low) < 20 and any(p in low for p in ["hi", "hello", "hey", "help"]):
        return (f"Hi! I'm the CareerAI assistant. Ask me to explain any module (Resume Analyzer, Job Matcher, "
                f"Skill Gap Analysis, Mock Interview, Interview Evaluation, Career Roadmap, Dashboard), "
                f"tell you what to do next, or summarize your session. Right now you're on **{here['label']}**.")

    # fallback — still page + data aware, not a canned line
    lines = _progress_lines(snap)
    return (
        f"I'm not fully sure what you mean, but here's what I know: you're on **{here['label']}** "
        f"({here['desc']})\n\nYour session so far:\n" + "\n".join(f"- {l}" for l in lines) +
        "\n\nTry asking things like *\"what should I do next?\"*, *\"what is Skill Gap Analysis?\"*, "
        "or *\"summarize my progress\"*."
    )


def render_chatbot(page_key: str = "home"):
    """Render the small '🤖 Ask CareerAI' assistant in the sidebar. Call once per page."""
    if "chatbot_history" not in st.session_state:
        st.session_state["chatbot_history"] = []

    with st.sidebar:
        st.markdown("---")
        popover_fn = getattr(st, "popover", None)
        box = popover_fn("🤖 Ask CareerAI", use_container_width=True) if popover_fn else st.expander("🤖 Ask CareerAI")
        with box:
            st.caption("Ask about any module or what to do next — answers use your live session data.")

            for role, msg in st.session_state["chatbot_history"][-8:]:
                prefix = "**You:**" if role == "user" else "**🤖 CareerAI:**"
                st.markdown(f"{prefix} {msg}")

            with st.form(key=f"chatbot_form_{page_key}", clear_on_submit=True):
                user_text = st.text_input(
                    "Your question", placeholder="e.g. what should I do next?", label_visibility="collapsed",
                )
                sent = st.form_submit_button("Ask")

            if sent and user_text.strip():
                reply = _answer(user_text, page_key)
                st.session_state["chatbot_history"].append(("user", user_text.strip()))
                st.session_state["chatbot_history"].append(("bot", reply))
                st.rerun()

            if st.session_state["chatbot_history"]:
                if st.button("Clear chat", key=f"chatbot_clear_{page_key}"):
                    st.session_state["chatbot_history"] = []
                    st.rerun()
