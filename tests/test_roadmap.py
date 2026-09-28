"""
tests/test_roadmap.py
========================
Unit tests for roadmap/roadmap_generator.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.scoring import SkillGapItem
from roadmap.roadmap_generator import prioritize_skills, build_weekly_plan, generate_roadmap


def _sample_gap_items():
    return [
        SkillGapItem(skill="Docker", status="Missing", importance="High"),
        SkillGapItem(skill="Java", status="Partial Match", importance="Medium"),
        SkillGapItem(skill="Python", status="Strong Match", importance="High"),
    ]


def test_prioritize_skills_excludes_strong_matches():
    items = prioritize_skills(_sample_gap_items())
    skill_names = [i.skill for i in items]
    assert "Python" not in skill_names
    assert "Docker" in skill_names
    assert "Java" in skill_names


def test_prioritize_skills_ranks_missing_high_importance_first():
    items = prioritize_skills(_sample_gap_items())
    assert items[0].skill == "Docker"  # High importance + Missing > Medium + Partial


def test_interview_weakness_bonus_increases_priority():
    items_without_bonus = prioritize_skills(_sample_gap_items())
    items_with_bonus = prioritize_skills(_sample_gap_items(), weak_interview_concepts=["Java"])

    java_without = next(i for i in items_without_bonus if i.skill == "Java")
    java_with = next(i for i in items_with_bonus if i.skill == "Java")
    assert java_with.priority_score > java_without.priority_score


def test_build_weekly_plan_creates_requested_number_of_weeks():
    items = prioritize_skills(_sample_gap_items())
    plan = build_weekly_plan(items, num_weeks=4, topics_per_week=3)
    assert len(plan) == 4
    for week in plan:
        assert len(week.topics) >= 1


def test_generate_roadmap_returns_expected_keys():
    roadmap = generate_roadmap(_sample_gap_items(), num_weeks=3)
    assert "prioritized_skills" in roadmap
    assert "weekly_plan" in roadmap
    assert len(roadmap["weekly_plan"]) == 3
