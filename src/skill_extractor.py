"""
Skill Extractor Module.
Extracts and categorizes technical and professional skills from resumes and job descriptions.
Supports skill aliases, acronym expansions, and category classification.
"""

import json
import os
import re
from typing import Dict, List, Set, Any

SKILL_ALIASES = {
    "restful apis": ["restful apis", "rest apis", "rest api", "restful api", "rest", "restful"],
    "rest apis": ["rest apis", "restful apis", "rest api", "restful api", "rest"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "postgresql": ["postgresql", "postgres"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud platform", "google cloud"],
    "azure": ["azure", "microsoft azure"],
    "nlp": ["nlp", "natural language processing"],
    "ci/cd": ["ci/cd", "ci cd", "continuous integration", "cicd"],
    "microservices architecture": ["microservices architecture", "microservices", "microservice architecture", "microservice"],
    "data analysis": ["data analysis", "data analyst", "data analytics"],
    "data cleaning": ["data cleaning", "data wrangling", "data preprocessing"],
    "deep learning": ["deep learning", "neural networks", "deep neural networks"],
    "machine learning": ["machine learning", "ml"],
    "object-oriented programming": ["object-oriented programming", "oop", "object oriented programming"]
}


def load_skills_dictionary(dict_path: str = None) -> Dict[str, List[str]]:
    """Loads the categorized skills dictionary from JSON."""
    if dict_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dict_path = os.path.join(current_dir, "data", "skills_dictionary.json")

    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def is_skill_in_text(skill_term: str, text: str) -> bool:
    """Checks if a skill or any of its known aliases appear in text."""
    lower_text = text.lower()
    lower_term = skill_term.lower().strip()

    # Candidates terms to test: the term itself + any aliases
    candidates = [lower_term]
    if lower_term in SKILL_ALIASES:
        candidates.extend(SKILL_ALIASES[lower_term])

    for cand in candidates:
        escaped = re.escape(cand)
        prefix = r'(?:\b|^)' if cand[0].isalnum() else r''
        suffix = r'(?:\b|$)' if cand[-1].isalnum() else r''
        pattern = rf'{prefix}{escaped}{suffix}'
        if re.search(pattern, lower_text):
            return True

    return False


def extract_skills_from_text(text: str, skills_dict: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """
    Extracts all known skills from raw or cleaned text using accurate boundary matching.
    """
    if skills_dict is None:
        skills_dict = load_skills_dictionary()

    found_skills: Set[str] = set()
    categorized: Dict[str, List[str]] = {cat: [] for cat in skills_dict.keys()}

    for category, skill_list in skills_dict.items():
        for skill in skill_list:
            if is_skill_in_text(skill, text):
                found_skills.add(skill)
                categorized[category].append(skill)

    cleaned_categorized = {k: v for k, v in categorized.items() if len(v) > 0}

    return {
        "all_skills": sorted(list(found_skills)),
        "categorized_skills": cleaned_categorized,
        "total_count": len(found_skills)
    }


def match_skills(candidate_skills_or_text: Any, required_skills: List[str]) -> Dict[str, Any]:
    """
    Compares candidate skills (or resume text) with required job skills.
    Handles exact names, case insensitivity, and common aliases.
    """
    matched = []
    missing = []

    if isinstance(candidate_skills_or_text, str):
        resume_text = candidate_skills_or_text
        cand_set = {s.lower() for s in extract_skills_from_text(resume_text)["all_skills"]}
    else:
        cand_set = {s.lower() for s in candidate_skills_or_text}
        resume_text = " ".join(candidate_skills_or_text)

    for req in required_skills:
        req_clean = req.strip()
        if not req_clean:
            continue
        req_lower = req_clean.lower()

        # Check 1: In candidate extracted skills set
        if req_lower in cand_set:
            matched.append(req_clean)
            continue

        # Check 2: Check aliases in extracted skills
        if req_lower in SKILL_ALIASES:
            alias_found = any(alias in cand_set for alias in SKILL_ALIASES[req_lower])
            if alias_found:
                matched.append(req_clean)
                continue

        # Check 3: Direct check against text
        if is_skill_in_text(req_clean, resume_text):
            matched.append(req_clean)
        else:
            missing.append(req_clean)

    total_req = len(required_skills)
    overlap_pct = (len(matched) / total_req * 100) if total_req > 0 else 0.0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "matched_count": len(matched),
        "required_count": total_req,
        "skill_match_percentage": round(overlap_pct, 2)
    }
