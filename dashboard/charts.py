"""
dashboard/charts.py
======================
Reusable Plotly chart builders for MODULE 8 (AI Career Dashboard).
Kept separate from Streamlit page code so charts can be unit-tested /
reused across multiple pages (Job Matcher, Skill Gap, Dashboard, etc.)
"""

from typing import Dict, List

import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------------------------
# Shared dark theme so every chart matches the app's navy/purple design
# system (utils/theme.py), instead of Plotly's default white background.
# ---------------------------------------------------------------------------
_PAPER_BG = "rgba(0,0,0,0)"
_PLOT_BG = "rgba(0,0,0,0)"
_FONT_COLOR = "#e8ecf6"
_GRID_COLOR = "rgba(255,255,255,0.08)"


def _apply_dark(fig: go.Figure) -> go.Figure:
    """Apply the shared dark/transparent styling to any Plotly figure in-place."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_PLOT_BG,
        font=dict(color=_FONT_COLOR),
        title_font=dict(color="#f5f7ff", size=16),
    )
    fig.update_xaxes(gridcolor=_GRID_COLOR, zerolinecolor=_GRID_COLOR)
    fig.update_yaxes(gridcolor=_GRID_COLOR, zerolinecolor=_GRID_COLOR)
    return fig


def gauge_chart(value: float, title: str, max_value: float = 100.0) -> go.Figure:
    """A gauge/speedometer chart for a single 0-100 score (e.g. Overall Job Match)."""
    color = "#34d399" if value >= 70 else ("#fbbf24" if value >= 40 else "#fb7185")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            number={"font": {"color": "#f5f7ff"}},
            gauge={
                "axis": {"range": [0, max_value], "tickcolor": "#e8ecf6"},
                "bar": {"color": color},
                "bgcolor": "rgba(255,255,255,0.04)",
                "bordercolor": "rgba(255,255,255,0.12)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(251,113,133,0.12)"},
                    {"range": [40, 70], "color": "rgba(251,191,36,0.12)"},
                    {"range": [70, max_value], "color": "rgba(52,211,153,0.12)"},
                ],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return _apply_dark(fig)


def skill_match_bar_chart(matched: int, partial: int, missing: int) -> go.Figure:
    """Bar chart summarizing matched / partial / missing skill counts."""
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Strong Match", "Partial Match", "Missing"],
                y=[matched, partial, missing],
                marker_color=["#34d399", "#fbbf24", "#fb7185"],
                text=[matched, partial, missing],
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title="Skill Match Overview",
        yaxis_title="Number of Skills",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return _apply_dark(fig)


def skill_gap_pie_chart(matched: int, partial: int, missing: int) -> go.Figure:
    labels = ["Strong Match", "Partial Match", "Missing"]
    values = [matched, partial, missing]
    fig = px.pie(
        names=labels,
        values=values,
        color=labels,
        color_discrete_map={
            "Strong Match": "#34d399",
            "Partial Match": "#fbbf24",
            "Missing": "#fb7185",
        },
        hole=0.45,
        title="Skill Gap Distribution",
    )
    fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    fig.update_traces(textfont=dict(color="#f5f7ff"))
    return _apply_dark(fig)


def job_match_radar_chart(semantic_pct: float, overlap_pct: float, coverage_pct: float) -> go.Figure:
    categories = ["Semantic Similarity", "Skill Overlap", "Resume Skill Coverage"]
    values = [semantic_pct, overlap_pct, coverage_pct]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name="Job Match")
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="Job Match Breakdown",
        height=380,
        margin=dict(l=30, r=30, t=50, b=20),
    )
    fig.update_traces(line_color="#a855f7", fillcolor="rgba(168,85,247,0.28)")
    return _apply_dark(fig)


def interview_performance_bar(category_scores: Dict[str, float]) -> go.Figure:
    """Bar chart of average score (/10) per interview question category."""
    if not category_scores:
        categories, scores = [], []
    else:
        categories = list(category_scores.keys())
        scores = list(category_scores.values())

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=scores,
                marker_color="#2563eb",
                text=[f"{s:.1f}" for s in scores],
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title="Interview Performance by Category",
        yaxis_title="Average Score (out of 10)",
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return _apply_dark(fig)


def technical_vs_hr_chart(category_scores: Dict[str, float]) -> go.Figure:
    """
    Groups category scores into a simplified Technical vs Non-Technical
    (HR/Behavioral) comparison view.
    """
    technical_cats = {"Technical", "Project-Based", "Scenario-Based"}
    non_technical_cats = {"HR", "Behavioral"}

    tech_scores = [v for k, v in category_scores.items() if k in technical_cats]
    nontech_scores = [v for k, v in category_scores.items() if k in non_technical_cats]

    tech_avg = sum(tech_scores) / len(tech_scores) if tech_scores else 0
    nontech_avg = sum(nontech_scores) / len(nontech_scores) if nontech_scores else 0

    fig = go.Figure(
        data=[
            go.Bar(
                x=["Technical / Project / Scenario", "HR / Behavioral"],
                y=[tech_avg, nontech_avg],
                marker_color=["#a855f7", "#06b6d4"],
                text=[f"{tech_avg:.1f}", f"{nontech_avg:.1f}"],
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title="Technical vs HR/Behavioral Performance",
        yaxis_title="Average Score (out of 10)",
        yaxis_range=[0, 10],
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return _apply_dark(fig)


def roadmap_progress_chart(weekly_plan: List[Dict]) -> go.Figure:
    """Horizontal bar chart showing number of topics scheduled per week."""
    weeks = [f"Week {w['week']}" for w in weekly_plan]
    counts = [len(w["topics"]) for w in weekly_plan]

    fig = go.Figure(
        data=[
            go.Bar(
                y=weeks,
                x=counts,
                orientation="h",
                marker_color="#2563eb",
                text=counts,
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title="Learning Roadmap — Topics per Week",
        xaxis_title="Number of Topics",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return _apply_dark(fig)
