"""
nlp/skill_extractor.py
========================
Dictionary-driven + fuzzy-matching skill extraction.

Design note (important for the viva):
This module is a RULE-BASED / lexical NLP component, not a trained ML
classifier. It uses:
  1. An external, maintainable skill dictionary (data/skills.csv) with
     canonical names + aliases, so new skills can be added without
     touching code.
  2. Regex word-boundary matching over normalized text (handles aliases,
     punctuation variants like "C++", "Node.js").
  3. difflib-based fuzzy matching as a second pass to catch minor
     spelling variants that are not explicitly listed as aliases
     (e.g. "Djnago" -> "Django"), which adds a small amount of
     approximate/"fuzzy AI" behaviour on top of pure dictionary lookup.

It deliberately does NOT claim to be a deep-learning NER model — that
distinction is reported plainly in the About page.
"""

import csv
import difflib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from nlp.text_preprocessor import normalize_for_matching


@dataclass
class SkillMatch:
    skill: str
    category: str
    matched_text: str
    match_type: str  # "exact", "alias", "fuzzy"


class SkillExtractor:
    """Loads the skill dictionary once and exposes extraction methods."""

    def __init__(self, skills_csv_path: str):
        self.skills_csv_path = skills_csv_path
        self.skill_to_category: Dict[str, str] = {}
        # alias (normalized) -> canonical skill name
        self.alias_lookup: Dict[str, str] = {}
        self._load_dictionary()

    def _load_dictionary(self) -> None:
        with open(self.skills_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = row["skill"].strip()
                category = row.get("category", "General").strip() or "General"
                self.skill_to_category[skill] = category

                canonical_norm = normalize_for_matching(skill)
                self.alias_lookup[canonical_norm] = skill

                aliases = row.get("aliases", "") or ""
                for alias in aliases.split("|"):
                    alias = alias.strip()
                    if alias:
                        self.alias_lookup[normalize_for_matching(alias)] = skill

    @property
    def all_skills(self) -> List[str]:
        return sorted(self.skill_to_category.keys())

    def extract(self, text: str, fuzzy: bool = True, fuzzy_cutoff: float = 0.87) -> List[SkillMatch]:
        """
        Extract skills mentioned in `text`.

        Returns a de-duplicated list of SkillMatch (one per canonical skill,
        keeping the strongest match type found).
        """
        if not text:
            return []

        norm_text = normalize_for_matching(text)
        found: Dict[str, SkillMatch] = {}

        # --- Pass 1: exact / alias word-boundary matching -------------------
        for alias_norm, canonical in self.alias_lookup.items():
            # Escape regex special chars but keep + and # and . meaningful
            pattern = r"(?<![a-z0-9])" + re.escape(alias_norm).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
            if re.search(pattern, norm_text):
                match_type = "exact" if normalize_for_matching(canonical) == alias_norm else "alias"
                # Prefer exact over alias if both would match
                if canonical not in found or found[canonical].match_type != "exact":
                    found[canonical] = SkillMatch(
                        skill=canonical,
                        category=self.skill_to_category.get(canonical, "General"),
                        matched_text=alias_norm,
                        match_type=match_type,
                    )

        # --- Pass 2: fuzzy matching on individual tokens/bigrams -------------
        if fuzzy:
            tokens = norm_text.split()
            candidates = tokens + [
                f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)
            ]
            alias_keys = list(self.alias_lookup.keys())
            for cand in set(candidates):
                if len(cand) < 3:
                    continue
                close = difflib.get_close_matches(cand, alias_keys, n=1, cutoff=fuzzy_cutoff)
                if close:
                    canonical = self.alias_lookup[close[0]]
                    if canonical not in found:
                        found[canonical] = SkillMatch(
                            skill=canonical,
                            category=self.skill_to_category.get(canonical, "General"),
                            matched_text=cand,
                            match_type="fuzzy",
                        )

        return sorted(found.values(), key=lambda m: (m.category, m.skill))

    def extract_names(self, text: str, **kwargs) -> List[str]:
        return [m.skill for m in self.extract(text, **kwargs)]


# ---------------------------------------------------------------------------
# Module-level singleton loader (so app.py / pages can just import a ready
# instance rather than re-reading the CSV on every call).
# ---------------------------------------------------------------------------
_EXTRACTOR_INSTANCE = None


def get_skill_extractor(skills_csv_path: str) -> SkillExtractor:
    global _EXTRACTOR_INSTANCE
    if _EXTRACTOR_INSTANCE is None:
        _EXTRACTOR_INSTANCE = SkillExtractor(skills_csv_path)
    return _EXTRACTOR_INSTANCE
