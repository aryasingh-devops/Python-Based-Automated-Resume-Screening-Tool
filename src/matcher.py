"""
Resume Matching & Scoring Engine.
Computes TF-IDF vectorization, Cosine Similarity, Skill Overlap, and Hybrid ATS Match Score.
"""

from typing import Dict, List, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.cleaner import clean_text
from src.skill_extractor import match_skills, extract_skills_from_text


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Computes cosine similarity between resume text and job description
    using TF-IDF Vectorizer with unigrams and bigrams.
    """
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(jd_text)

    if not cleaned_resume.strip() or not cleaned_jd.strip():
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf_matrix = vectorizer.fit_transform([cleaned_jd, cleaned_resume])

    # Cosine similarity between row 0 (JD) and row 1 (Resume)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))


def compute_hybrid_score(
    resume_text: str,
    jd_text: str,
    required_skills: List[str],
    preferred_skills: List[str] = None,
    skill_weight: float = 0.60,
    tfidf_weight: float = 0.40,
    job_title: str = ""
) -> Dict[str, Any]:
    """
    Computes a comprehensive industry-grade ATS score:
    - Skill Match Score (60% default weight)
    - TF-IDF Cosine Similarity (40% default weight)
    - Preferred Skill Bonus (up to +5% capped at 100%)
    """
    if preferred_skills is None:
        preferred_skills = []

    # Construct rich JD corpus including title, mandatory skills, preferred skills, and description
    rich_jd_corpus = f"{job_title} {' '.join(required_skills)} {' '.join(preferred_skills)} {jd_text}"

    # 1. TF-IDF Cosine Similarity
    tfidf_sim = compute_tfidf_similarity(resume_text, rich_jd_corpus)
    tfidf_score_pct = round(tfidf_sim * 100, 2)

    # 2. Extract Candidate Skills and Categories
    cand_skill_analysis = extract_skills_from_text(resume_text)
    cand_skills = cand_skill_analysis["all_skills"]

    # 3. Match Required Skills (using both extracted skills and text analysis)
    req_match = match_skills(resume_text, required_skills)
    skill_pct = req_match["skill_match_percentage"]

    # 4. Match Preferred Skills
    pref_match = match_skills(resume_text, preferred_skills) if preferred_skills else {
        "matched_skills": [], "missing_skills": [], "skill_match_percentage": 0.0
    }

    # 5. Hybrid Weighted Score
    base_score = (skill_pct * skill_weight) + (tfidf_score_pct * tfidf_weight)

    # Preferred bonus: up to +5 points based on preferred skills ratio
    pref_bonus = 0.0
    if preferred_skills and len(preferred_skills) > 0:
        pref_ratio = len(pref_match["matched_skills"]) / len(preferred_skills)
        pref_bonus = round(pref_ratio * 5.0, 2)

    final_score = round(min(100.0, base_score + pref_bonus), 2)

    return {
        "final_score": final_score,
        "skill_score": skill_pct,
        "tfidf_score": tfidf_score_pct,
        "preferred_bonus": pref_bonus,
        "matched_required_skills": req_match["matched_skills"],
        "missing_required_skills": req_match["missing_skills"],
        "matched_preferred_skills": pref_match["matched_skills"],
        "detected_skills": cand_skills,
        "categorized_skills": cand_skill_analysis["categorized_skills"]
    }
