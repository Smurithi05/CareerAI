"""
roadmap/roadmap_generator.py
==============================
MODULE 7: Personalized Career Roadmap generator.

This is a RULE-BASED prioritization + scheduling algorithm (not a trained
ML model). It combines:
  - skill-gap results (Module 4): missing / partial skills, with importance
  - interview weaknesses (Module 6/feedback.py): weak concepts/categories
into a single priority-ranked list, then distributes that list across a
fixed number of weeks, mixing in recurring "Mock Interview Practice" and
"Project Practice" blocks — mirroring the example roadmap structure in
the project specification.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models.scoring import SkillGapItem, get_recommendation


@dataclass
class RoadmapItem:
    skill: str
    priority_score: float
    reason: str
    recommendation: str


@dataclass
class WeeklyPlan:
    week: int
    topics: List[str] = field(default_factory=list)
    focus: str = ""


IMPORTANCE_WEIGHT = {"High": 3, "Medium": 2, "Low": 1}
STATUS_WEIGHT = {"Missing": 3, "Partial Match": 2, "Strong Match": 0}


def prioritize_skills(
    skill_gap_items: List[SkillGapItem],
    weak_interview_concepts: Optional[List[str]] = None,
) -> List[RoadmapItem]:
    """
    Compute a priority score per skill:
        priority = importance_weight * status_weight
                 + interview_weakness_bonus (if the skill/concept also
                   showed up as a weak area during the mock interview)
    Higher score = should be studied sooner.
    """
    weak_interview_concepts = weak_interview_concepts or []
    weak_lower = {c.lower() for c in weak_interview_concepts}

    items = []
    for gap in skill_gap_items:
        if gap.status == "Strong Match":
            continue  # already strong — no roadmap entry needed

        base = IMPORTANCE_WEIGHT.get(gap.importance, 1) * STATUS_WEIGHT.get(gap.status, 1)
        bonus = 2 if gap.skill.lower() in weak_lower else 0
        priority = base + bonus

        reason_parts = [f"{gap.status} for a {gap.importance}-importance job requirement"]
        if bonus:
            reason_parts.append("also flagged as a weak area during your mock interview")
        reason = "; ".join(reason_parts)

        items.append(
            RoadmapItem(
                skill=gap.skill,
                priority_score=priority,
                reason=reason,
                recommendation=get_recommendation(gap.skill),
            )
        )

    items.sort(key=lambda i: i.priority_score, reverse=True)
    return items


def build_weekly_plan(
    prioritized_items: List[RoadmapItem],
    num_weeks: int = 4,
    topics_per_week: int = 3,
) -> List[WeeklyPlan]:
    """
    Distribute prioritized skills across weeks (highest priority first),
    then append recurring practice blocks in the final week, matching the
    example structure given in the specification (mock interviews +
    project practice towards the end).
    """
    weeks: List[WeeklyPlan] = [WeeklyPlan(week=i + 1) for i in range(num_weeks)]

    slot = 0
    total_slots = num_weeks * topics_per_week
    for item in prioritized_items[: max(total_slots - num_weeks, 0)] if num_weeks > 1 else prioritized_items[:total_slots]:
        week_idx = slot % num_weeks
        if len(weeks[week_idx].topics) < topics_per_week:
            weeks[week_idx].topics.append(item.skill)
        slot += 1

    # Ensure every week has at least a filler if there weren't enough gap skills
    for w in weeks:
        if not w.topics:
            w.topics.append("Revision of core fundamentals")

    # Add recurring practice blocks
    for i, w in enumerate(weeks):
        if i == len(weeks) - 2 and len(weeks) >= 2:
            w.topics.append("Mock Interviews (Technical)")
        if i == len(weeks) - 1:
            w.topics.append("Project Practice")
            w.topics.append("Mock Interviews (HR + Technical)")
        w.focus = ", ".join(w.topics)

    return weeks


def generate_roadmap(
    skill_gap_items: List[SkillGapItem],
    weak_interview_concepts: Optional[List[str]] = None,
    num_weeks: int = 4,
) -> Dict:
    """
    Full Module 7 entry point returning both the prioritized skill list
    (with recommendations) and the week-by-week schedule.
    """
    prioritized = prioritize_skills(skill_gap_items, weak_interview_concepts)
    weekly_plan = build_weekly_plan(prioritized, num_weeks=num_weeks)

    return {
        "prioritized_skills": [
            {
                "skill": p.skill,
                "priority_score": p.priority_score,
                "reason": p.reason,
                "recommendation": p.recommendation,
            }
            for p in prioritized
        ],
        "weekly_plan": [
            {"week": w.week, "topics": w.topics, "focus": w.focus} for w in weekly_plan
        ],
    }
