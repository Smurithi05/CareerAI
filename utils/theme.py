"""
utils/theme.py
================
Shared visual design system for CareerAI.

This module is the SINGLE place that defines the app's "modern AI SaaS
dashboard" look (deep navy background, purple/electric-blue/cyan gradient
accents, glass-morphism cards, gradient metric tiles, pipeline diagrams).
Every page imports `inject_theme()` once at the top so the whole app has
one consistent identity instead of Streamlit's default look.

Keeping this in one module (instead of copy-pasting CSS into every page)
is also the reason a full visual re-skin of the app only required editing
this one file plus each page's content layout.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palette (kept in one place so it's easy to explain / tweak)
# ---------------------------------------------------------------------------
NAVY = "#0b1020"
NAVY_2 = "#121933"
PURPLE = "#7c3aed"
VIOLET = "#a855f7"
BLUE = "#2563eb"
CYAN = "#06b6d4"
GRADIENT = f"linear-gradient(135deg, {BLUE} 0%, {PURPLE} 55%, {CYAN} 100%)"
GRADIENT_SOFT = f"linear-gradient(135deg, rgba(37,99,235,0.15) 0%, rgba(124,58,237,0.15) 55%, rgba(6,182,212,0.15) 100%)"


def inject_theme():
    """Inject the global CSS design system. Call once near the top of every page."""
    st.markdown(
        f"""
        <style>
        /* ---- App background ------------------------------------------------ */
        .stApp {{
            background: radial-gradient(circle at 15% 0%, #1a2140 0%, {NAVY} 45%, #060811 100%);
        }}
        section[data-testid="stSidebar"] {{
            background: {NAVY_2};
            border-right: 1px solid rgba(255,255,255,0.06);
        }}
        html, body, [class*="css"] {{
            color: #e8ecf6;
        }}

        /* ---- Headings -------------------------------------------------------- */
        h1, h2, h3 {{
            color: #f5f7ff !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }}
        p, li, span, label {{ color:grey; }}

        /* ---- Hero ------------------------------------------------------------ */
        .cai-hero {{
            background: {GRADIENT};
            border-radius: 22px;
            padding: 48px 40px;
            margin-bottom: 28px;
            box-shadow: 0 20px 60px rgba(90, 60, 220, 0.35);
            position: relative;
            overflow: hidden;
        }}
        .cai-hero h1 {{
            color: white !important;
            font-size: 2.6rem !important;
            margin-bottom: 6px !important;
        }}
        .cai-hero p {{
            color: rgba(255,255,255,0.92) !important;
            font-size: 1.05rem;
            max-width: 720px;
        }}
        .cai-hero .cai-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.35);
            color: white;
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 14px;
        }}

        /* ---- Glass card -------------------------------------------------------- */
        .cai-card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.09);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 22px 20px;
            height: 100%;
        }}
        .cai-card h4 {{ margin-top: 0; color: #f5f7ff; }}

        /* ---- Gradient metric tile ---------------------------------------------- */
        .cai-metric {{
            background: {GRADIENT};
            border-radius: 16px;
            padding: 18px 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(90, 60, 220, 0.25);
        }}
        .cai-metric .cai-metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: white;
            line-height: 1.1;
        }}
        .cai-metric .cai-metric-label {{
            font-size: 0.82rem;
            color: rgba(255,255,255,0.9);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 4px;
        }}

        /* ---- Status pill -------------------------------------------------------- */
        .cai-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        .cai-pill-on {{ background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }}
        .cai-pill-off {{ background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.4); }}

        /* ---- Pipeline step ------------------------------------------------------- */
        .cai-pipe-step {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 14px;
            padding: 14px 10px;
            text-align: center;
            font-weight: 600;
            font-size: 0.85rem;
            color: #f5f7ff;
        }}
        .cai-pipe-emoji {{ font-size: 1.6rem; display: block; margin-bottom: 4px; }}
        .cai-pipe-arrow {{
            text-align: center;
            font-size: 1.4rem;
            color: {CYAN};
            padding-top: 18px;
        }}

        /* ---- Buttons ------------------------------------------------------------- */
        .stButton > button {{
            background: {GRADIENT};
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            padding: 0.6em 1.2em;
            box-shadow: 0 6px 18px rgba(90, 60, 220, 0.3);
        }}
        .stButton > button:hover {{
            filter: brightness(1.08);
            color: white;
        }}

        /* ---- Tag / skill chip ------------------------------------------------------ */
        .cai-chip {{
            display: inline-block;
            background: rgba(37,99,235,0.15);
            border: 1px solid rgba(37,99,235,0.4);
            color: #93c5fd;
            padding: 3px 11px;
            border-radius: 999px;
            font-size: 0.82rem;
            margin: 3px 4px 3px 0;
        }}
        .cai-chip-missing {{
            background: rgba(244,63,94,0.12);
            border-color: rgba(244,63,94,0.4);
            color: #fda4af;
        }}
        .cai-chip-partial {{
            background: rgba(245,158,11,0.12);
            border-color: rgba(245,158,11,0.4);
            color: #fcd34d;
        }}

        /* ---- AI badge ------------------------------------------------------------- */
        .cai-ai-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: {GRADIENT};
            color: white;
            padding: 4px 13px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            box-shadow: 0 4px 14px rgba(90, 60, 220, 0.35);
        }}

        /* ---- Page header ------------------------------------------------------------ */
        .cai-page-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding-bottom: 14px;
            margin-bottom: 22px;
        }}
        .cai-page-header h1 {{
            font-size: 1.9rem !important;
            margin: 0 !important;
        }}
        .cai-page-header .cai-module-tag {{
            font-size: 0.8rem;
            color: #93c5fd;
            font-weight: 600;
        }}
        .cai-page-caption {{ color: #9aa4c4; margin-top: -6px; margin-bottom: 18px; }}

        /* ---- Section header ---------------------------------------------------------- */
        .cai-section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 26px 0 12px 0;
            font-size: 1.25rem;
            font-weight: 800;
            color: #f5f7ff;
        }}
        .cai-section-header .cai-section-num {{
            background: {GRADIENT};
            color: white;
            width: 26px; height: 26px;
            border-radius: 8px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 0.85rem;
        }}

        /* ---- Info / disclaimer card --------------------------------------------------- */
        .cai-info-card {{
            border-radius: 14px;
            padding: 14px 18px;
            margin: 12px 0;
            border: 1px solid;
            font-size: 0.92rem;
        }}
        .cai-info-neutral {{ background: rgba(37,99,235,0.10); border-color: rgba(37,99,235,0.35); color: #bfdbfe; }}
        .cai-info-success {{ background: rgba(16,185,129,0.10); border-color: rgba(16,185,129,0.35); color: #a7f3d0; }}
        .cai-info-warning {{ background: rgba(245,158,11,0.10); border-color: rgba(245,158,11,0.35); color: #fde68a; }}
        .cai-info-danger  {{ background: rgba(244,63,94,0.10);  border-color: rgba(244,63,94,0.35);  color: #fecdd3; }}

        /* ---- Footer -------------------------------------------------------------------- */
        .cai-footer {{
            margin-top: 46px;
            padding-top: 18px;
            border-top: 1px solid rgba(255,255,255,0.08);
            text-align: center;
            color: #6b7394;
            font-size: 0.82rem;
        }}

        /* ================================================================
           NATIVE STREAMLIT WIDGET OVERRIDES — keep every page consistent
           ================================================================ */

        /* Alert boxes (st.info / st.success / st.warning / st.error) */
        div[data-testid="stAlert"] {{
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            backdrop-filter: blur(6px);
        }}

        /* Expanders */
        details[data-testid="stExpander"], .streamlit-expanderHeader {{
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            border-radius: 14px !important;
        }}
        summary {{ color: #f5f7ff !important; font-weight: 600 !important; }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            color: #9aa4c4 !important;
            font-weight: 600 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #f5f7ff !important;
            border-bottom: 3px solid {CYAN} !important;
        }}
        div[data-baseweb="tab-highlight"] {{ background-color: {CYAN} !important; }}
        div[data-baseweb="tab-border"] {{ background-color: rgba(255,255,255,0.08) !important; }}

        /* Dataframes / tables */
        div[data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.09);
        }}

        /* Text areas / text inputs / selectboxes */
        .stTextArea textarea, .stTextInput input, div[data-baseweb="select"] > div {{
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.14) !important;
            border-radius: 10px !important;
            color: #f5f7ff !important;
        }}

        /* Fix: on some Streamlit versions the actual widget chrome (the div
           wrapping the <textarea>/<input>) keeps the light-theme background
           from .streamlit/config.toml even though the text color above is
           set to near-white for the dark app background — making typed
           text invisible (white-on-white). Force both the wrapper and the
           leaf element to the same dark background + light text so this
           can't happen, and make placeholder text visible too. */
        .stTextArea textarea,
        .stTextInput input,
        div[data-baseweb="textarea"],
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="input"],
        div[data-baseweb="input"] > div {{
            background-color: #141a33 !important;
            color: #f5f7ff !important;
            -webkit-text-fill-color: #f5f7ff !important;
            caret-color: #f5f7ff !important;
        }}
        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {{
            color: #8891b0 !important;
            opacity: 1 !important;
        }}

        /* File uploader dropzone */
        section[data-testid="stFileUploaderDropzone"] {{
            background: {GRADIENT_SOFT} !important;
            border: 1.5px dashed rgba(168,85,247,0.55) !important;
            border-radius: 16px !important;
        }}

        /* Progress bar */
        div[role="progressbar"] > div {{ background: {GRADIENT} !important; }}

        /* Metrics (st.metric) — used sparingly, still re-skin so it fits */
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 14px;
            padding: 10px 14px;
        }}
        div[data-testid="stMetricLabel"] {{ color: #9aa4c4 !important; }}
        div[data-testid="stMetricValue"] {{ color: #f5f7ff !important; }}

        /* Slider */
        div[data-testid="stSlider"] [role="slider"] {{ background-color: {CYAN} !important; }}

        /* Links (st.page_link) */
        a[data-testid="stPageLink-NavLink"] {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px !important;
        }}
        
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Reusable page-building components
# ---------------------------------------------------------------------------

def render_page_header(icon: str, title: str, module_tag: str, caption: str):
    """Shared header used at the top of every module page (replaces st.title/st.caption)."""
    st.markdown(
        f"""
        <div class="cai-page-header">
            <h1>{icon} {title}</h1>
            <span class="cai-module-tag">{module_tag}</span>
        </div>
        <div class="cai-page-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(text: str, num=None):
    """Small gradient-numbered section heading used to break a page into steps."""
    num_html = f'<span class="cai-section-num">{num}</span>' if num is not None else ""
    st.markdown(f'<div class="cai-section-header">{num_html}{text}</div>', unsafe_allow_html=True)


def render_metric_card(col, value: str, label: str):
    """Alias of metric_tile — gradient metric tile inside a given column."""
    metric_tile(col, value, label)


def render_info_card(text: str, variant: str = "neutral"):
    """variant: 'neutral' | 'success' | 'warning' | 'danger'"""
    css = {"neutral": "cai-info-neutral", "success": "cai-info-success",
           "warning": "cai-info-warning", "danger": "cai-info-danger"}.get(variant, "cai-info-neutral")
    st.markdown(f'<div class="cai-info-card {css}">{text}</div>', unsafe_allow_html=True)


def render_ai_badge(text: str = "AI ANALYSIS"):
    st.markdown(f'<span class="cai-ai-badge">🧠 {text}</span>', unsafe_allow_html=True)


def render_progress_card(col, label: str, value_pct: float, help_text: str = ""):
    """A labeled progress bar inside a glass card — used for score breakdowns."""
    with col:
        st.markdown(f'<div class="cai-card"><h4 style="margin-bottom:6px;">{label}: {value_pct:.0f}%</h4>', unsafe_allow_html=True)
        st.progress(min(max(value_pct / 100, 0.0), 1.0))
        if help_text:
            st.caption(help_text)
        st.markdown("</div>", unsafe_allow_html=True)


def render_feature_card(col, emoji: str, title: str, desc: str, page_path: str = None, link_label: str = None):
    """Alias of the home page's workflow_card, usable from any page (nav card with optional link)."""
    with col:
        st.markdown(
            f"""<div class="cai-card"><h4>{emoji} {title}</h4><p style="font-size:0.9rem;">{desc}</p></div>""",
            unsafe_allow_html=True,
        )
        if page_path:
            st.page_link(page_path, label=link_label or f"Open {title} →")


def render_footer():
    st.markdown(
        '<div class="cai-footer">CareerAI &middot; Final-Year B.Tech Internship-II Project &middot; '
        'No paid APIs &middot; All data stored locally</div>',
        unsafe_allow_html=True,
    )


def skill_chips(skills, variant: str = "matched"):
    """Render a list of skills as chip badges. variant: 'matched' | 'partial' | 'missing'."""
    css_class = {"matched": "cai-chip", "partial": "cai-chip cai-chip-partial", "missing": "cai-chip cai-chip-missing"}.get(variant, "cai-chip")
    if not skills:
        st.caption("None")
        return
    html = "".join(f'<span class="{css_class}">{s}</span>' for s in skills)
    st.markdown(html, unsafe_allow_html=True)


def hero(title: str, subtitle: str, badge: str = "AI-Powered Career Intelligence Platform"):
    """Render the shared gradient hero banner."""
    st.markdown(
        f"""
        <div class="cai-hero">
            <div class="cai-badge">🧠 {badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_tile(col, value: str, label: str):
    """Render one gradient metric tile inside a given `st.columns()` slot."""
    with col:
        st.markdown(
            f"""
            <div class="cai-metric">
                <div class="cai-metric-value">{value}</div>
                <div class="cai-metric-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def status_pill(text: str, active: bool) -> str:
    css_class = "cai-pill-on" if active else "cai-pill-off"
    dot = "🟢" if active else "🟡"
    return f'<span class="cai-pill {css_class}">{dot} {text}</span>'


def pipeline(steps):
    """
    Render a horizontal AI pipeline diagram.
    `steps` is a list of (emoji, label) tuples, e.g. [("📄", "Resume"), ...]
    """
    n = len(steps)
    cols = st.columns(n * 2 - 1)
    for i, (emoji, label) in enumerate(steps):
        col_idx = i * 2
        with cols[col_idx]:
            st.markdown(
                f"""<div class="cai-pipe-step"><span class="cai-pipe-emoji">{emoji}</span>{label}</div>""",
                unsafe_allow_html=True,
            )
        if col_idx + 1 < len(cols):
            with cols[col_idx + 1]:
                st.markdown('<div class="cai-pipe-arrow">➜</div>', unsafe_allow_html=True)
