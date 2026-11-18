"""
Main Command Line Pipeline for Automated Resume Screening Tool.
Runs batch evaluation of resumes against a job description, calculates ATS scores,
generates a ranked decision table, and saves CSV and image reports.
"""

import os
import sys
import argparse
import json
from src.extractor import extract_resume_data
from src.matcher import compute_hybrid_score
from src.reporter import generate_candidate_report, export_to_csv, generate_visual_dashboard


def load_job_descriptions():
    """Loads default pre-configured job descriptions from data folder."""
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "job_descriptions.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def run_screening_pipeline(
    resumes_dir: str = None,
    job_key: str = "python_backend_developer",
    shortlist_threshold: float = 70.0,
    review_threshold: float = 50.0
):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if resumes_dir is None:
        resumes_dir = os.path.join(base_dir, "resumes")

    print("\n" + "=" * 70)
    print("      AUTOMATED RESUME SCREENING & ATS EVALUATION SYSTEM")
    print("=" * 70)

    # 1. Load Job Description
    job_db = load_job_descriptions()
    if job_key not in job_db:
        print(f"[Warning] Job key '{job_key}' not found. Defaulting to 'python_backend_developer'.")
        job_key = "python_backend_developer"

    jd_info = job_db[job_key]
    print(f"\n[Target Position] : {jd_info['title']} ({jd_info['department']})")
    print(f"[Experience Need] : {jd_info['experience_required']}")
    print(f"[Required Skills] : {', '.join(jd_info['required_skills'])}")
    print(f"[Preferred Skills]: {', '.join(jd_info.get('preferred_skills', []))}")
    print("-" * 70)

    # 2. Collect Resume Files
    if not os.path.exists(resumes_dir):
        print(f"[Error] Resumes directory not found: {resumes_dir}")
        return

    valid_extensions = {".pdf", ".docx", ".doc", ".txt"}
    files = [f for f in os.listdir(resumes_dir) if os.path.splitext(f)[1].lower() in valid_extensions]

    if not files:
        print(f"[Warning] No supported resume files found in '{resumes_dir}'.")
        print("Please place .pdf, .docx, or .txt files in the resumes/ directory.")
        return

    print(f"\n[Scanning] Found {len(files)} resumes in '{resumes_dir}'")
    evaluations = []

    # 3. Process Each Resume
    for idx, fname in enumerate(files, 1):
        fpath = os.path.join(resumes_dir, fname)
        resume_data = extract_resume_data(fpath)

        match_result = compute_hybrid_score(
            resume_text=resume_data["raw_text"],
            jd_text=jd_info["description"],
            required_skills=jd_info["required_skills"],
            preferred_skills=jd_info.get("preferred_skills", []),
            job_title=jd_info.get("title", "")
        )

        # Merge extracted metadata with scoring
        evaluation = {
            "candidate_name": resume_data["candidate_name"],
            "filename": fname,
            "email": resume_data["email"],
            "phone": resume_data["phone"],
            "final_score": match_result["final_score"],
            "skill_score": match_result["skill_score"],
            "tfidf_score": match_result["tfidf_score"],
            "matched_required_skills": match_result["matched_required_skills"],
            "missing_required_skills": match_result["missing_required_skills"]
        }
        evaluations.append(evaluation)
        print(f"  -> [{idx}/{len(files)}] Processed: {resume_data['candidate_name']} ({fname}) - Score: {match_result['final_score']}%")

    # 4. Generate Ranking Report
    df_report = generate_candidate_report(
        evaluations,
        shortlist_threshold=shortlist_threshold,
        review_threshold=review_threshold
    )

    # 5. Display Console Table
    print("\n" + "=" * 70)
    print("                    FINAL SCREENING RANKINGS")
    print("=" * 70)

    display_cols = ["Rank", "Candidate Name", "Status", "Final Score (%)", "Skill Match (%)", "TF-IDF Match (%)"]
    print(df_report[display_cols].to_string(index=False))

    # Summary Statistics
    counts = df_report["Status"].value_counts().to_dict()
    print("\n" + "-" * 70)
    print(f"DECISION SUMMARY : Shortlisted: {counts.get('Shortlisted', 0)} | "
          f"Under Review: {counts.get('Under Review', 0)} | "
          f"Rejected: {counts.get('Rejected', 0)}")
    print("-" * 70)

    # 6. Save Artifacts (CSV & Visualization)
    csv_path = export_to_csv(df_report)
    img_path = generate_visual_dashboard(df_report)

    print(f"\n[Generated Output] CSV Report       : {csv_path}")
    print(f"[Generated Output] Chart Dashboard  : {img_path}")
    print("\n[Browser UI Ready] To launch interactive Web App in browser:")
    print("  Run command: streamlit run app.py\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool CLI")
    parser.add_argument("--job", type=str, default="python_backend_developer",
                        choices=["python_backend_developer", "data_scientist", "data_analyst", "fullstack_python_developer"],
                        help="Select pre-configured target job description")
    parser.add_argument("--resumes", type=str, default=None, help="Custom folder containing resumes")
    parser.add_argument("--shortlist", type=float, default=70.0, help="Minimum score to Shortlist (default: 70)")
    parser.add_argument("--review", type=float, default=50.0, help="Minimum score for Review (default: 50)")

    args = parser.parse_args()
    run_screening_pipeline(
        resumes_dir=args.resumes,
        job_key=args.job,
        shortlist_threshold=args.shortlist,
        review_threshold=args.review
    )
