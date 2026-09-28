"""
interview/question_engine.py
==============================
MODULE 5: AI Mock Interview — question selection/generation engine.

This is a RULE-BASED question SELECTOR, not a generative language model:
questions are drawn from a structured, hand-curated question bank
(data/interview_questions.json) and dynamically chosen based on the
candidate profile (resume skills, projects, job role, missing skills).

No paid generative AI API is used or required.
"""

import json
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config import QUESTION_BANK_JSON


@dataclass
class InterviewQuestion:
    question: str
    category: str        # Technical | Project-Based | Behavioral | HR | Scenario-Based
    difficulty: str      # Easy | Medium | Hard
    concepts: List[str] = field(default_factory=list)
    related_skill: Optional[str] = None


class QuestionEngine:
    def __init__(self, question_bank_path: str = str(QUESTION_BANK_JSON)):
        with open(question_bank_path, "r", encoding="utf-8") as f:
            self.bank = json.load(f)

    # -- internal helpers ----------------------------------------------------
    def _generic_technical(self, difficulty: str) -> List[InterviewQuestion]:
        items = self.bank.get("generic_technical", {}).get(difficulty, [])
        return [
            InterviewQuestion(q["question"], "Technical", difficulty, q.get("concepts", []))
            for q in items
        ]

    def _skill_specific(self, skill: str, difficulty: str) -> List[InterviewQuestion]:
        skill_bank = self.bank.get("skill_specific", {}).get(skill, {})
        items = skill_bank.get(difficulty, [])
        return [
            InterviewQuestion(q["question"], "Technical", difficulty, q.get("concepts", []), related_skill=skill)
            for q in items
        ]

    def _hr(self, difficulty: str) -> List[InterviewQuestion]:
        items = self.bank.get("hr", {}).get(difficulty, [])
        return [InterviewQuestion(q["question"], "HR", difficulty, q.get("concepts", [])) for q in items]

    def _behavioral(self, difficulty: str) -> List[InterviewQuestion]:
        items = self.bank.get("behavioral", {}).get(difficulty, [])
        return [InterviewQuestion(q["question"], "Behavioral", difficulty, q.get("concepts", [])) for q in items]

    def _scenario(self, difficulty: str) -> List[InterviewQuestion]:
        items = self.bank.get("scenario", {}).get(difficulty, [])
        return [InterviewQuestion(q["question"], "Scenario-Based", difficulty, q.get("concepts", [])) for q in items]

    def _project_questions(self, projects: List[str], difficulty: str) -> List[InterviewQuestion]:
        templates = self.bank.get("project_template_questions", [])
        if not projects:
            return []
        results = []
        # Use up to 2 distinct projects to avoid an overly repetitive interview
        for project_line in projects[:2]:
            project_name = project_line.strip()[:60] or "your project"
            template = random.choice(templates)
            results.append(
                InterviewQuestion(
                    template.format(project=project_name),
                    "Project-Based",
                    difficulty,
                    concepts=["project architecture", "problem solving", "technology choice"],
                )
            )
        return results

    @staticmethod
    def _difficulty_pool(difficulty: str) -> List[str]:
        if difficulty == "Mixed":
            return ["Easy", "Medium", "Hard"]
        return [difficulty]

    # -- public API ------------------------------------------------------------
    def generate_questions(
        self,
        num_questions: int,
        difficulty: str,
        question_type: str,
        resume_skills: List[str],
        missing_skills: List[str],
        projects: List[str],
        job_role: str = "",
    ) -> List[InterviewQuestion]:
        """
        Build a question set tailored to the candidate.

        Strategy:
          - Prioritize skill-specific technical questions for skills the
            candidate DOES have (tests depth) and a couple from missing
            skills (tests awareness/learning ability).
          - Mix in project-based questions from the candidate's own resume.
          - Fill remaining slots with generic technical / HR / behavioral /
            scenario-based questions according to `question_type`.
          - Respect the requested difficulty (or "Mixed").
        """
        random.seed()  # allow variety between mock-interview attempts
        difficulty_pool = self._difficulty_pool(difficulty)
        candidates: List[InterviewQuestion] = []

        relevant_skills = [s for s in resume_skills if s in self.bank.get("skill_specific", {})]
        relevant_missing = [s for s in missing_skills if s in self.bank.get("skill_specific", {})]

        if question_type in ("Technical", "Mixed"):
            for skill in relevant_skills:
                for d in difficulty_pool:
                    candidates.extend(self._skill_specific(skill, d))
            for skill in relevant_missing[:2]:
                for d in ["Easy", "Medium"] if difficulty == "Mixed" else difficulty_pool:
                    candidates.extend(self._skill_specific(skill, d))
            for d in difficulty_pool:
                candidates.extend(self._generic_technical(d))
            for d in difficulty_pool:
                candidates.extend(self._project_questions(projects, d))
            for d in difficulty_pool:
                candidates.extend(self._scenario(d))

        if question_type in ("HR", "Mixed"):
            for d in difficulty_pool:
                candidates.extend(self._hr(d))
                candidates.extend(self._behavioral(d))

        # De-duplicate (same question text) while preserving order variety
        seen = set()
        unique_candidates = []
        for q in candidates:
            if q.question not in seen:
                seen.add(q.question)
                unique_candidates.append(q)

        random.shuffle(unique_candidates)

        if len(unique_candidates) < num_questions:
            # Backfill from the full bank regardless of type/difficulty filters
            # so the requested question count is still met wherever possible.
            all_possible: List[InterviewQuestion] = []
            for d in ["Easy", "Medium", "Hard"]:
                all_possible.extend(self._generic_technical(d))
                all_possible.extend(self._hr(d))
                all_possible.extend(self._behavioral(d))
                all_possible.extend(self._scenario(d))
            random.shuffle(all_possible)
            for q in all_possible:
                if q.question not in seen:
                    seen.add(q.question)
                    unique_candidates.append(q)
                if len(unique_candidates) >= num_questions:
                    break

        return unique_candidates[:num_questions]


_ENGINE_SINGLETON: Optional[QuestionEngine] = None


def get_question_engine() -> QuestionEngine:
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        _ENGINE_SINGLETON = QuestionEngine()
    return _ENGINE_SINGLETON
