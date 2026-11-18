"""
Screening Reporter & Ranking Module.
Ranks candidates, applies shortlist/review/reject criteria, exports CSV and generates visual dashboards.
"""

import os
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


def assign_decision(score: float, shortlist_threshold: float = 70.0, review_threshold: float = 50.0) -> str:
    """Assigns hiring recommendation status based on score thresholds."""
    if score >= shortlist_threshold:
        return "Shortlisted"
    elif score >= review_threshold:
        return "Under Review"
    else:
        return "Rejected"


def generate_candidate_report(
    evaluations: List[Dict[str, Any]],
    shortlist_threshold: float = 70.0,
    review_threshold: float = 50.0
) -> pd.DataFrame:
    """
    Takes a list of candidate evaluation dictionaries and creates a ranked pandas DataFrame.
    """
    rows = []
    for item in evaluations:
        status = assign_decision(item["final_score"], shortlist_threshold, review_threshold)
        rows.append({
            "Candidate Name": item.get("candidate_name", "Unknown"),
            "Status": status,
            "Final Score (%)": item["final_score"],
            "Skill Match (%)": item["skill_score"],
            "TF-IDF Match (%)": item["tfidf_score"],
            "Matched Skills": ", ".join(item["matched_required_skills"]),
            "Missing Skills": ", ".join(item["missing_required_skills"]),
            "Email": item.get("email", "N/A"),
            "Phone": item.get("phone", "N/A"),
            "Filename": item.get("filename", "")
        })

    df = pd.DataFrame(rows)
    # Sort descending by Final Score
    if not df.empty:
        df = df.sort_values(by="Final Score (%)", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", range(1, len(df) + 1))

    return df


def export_to_csv(df: pd.DataFrame, output_path: str = None) -> str:
    """Exports candidate rankings to a CSV file."""
    if output_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(current_dir, "outputs", "screening_report.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def generate_visual_dashboard(df: pd.DataFrame, output_image_path: str = None) -> str:
    """
    Generates and saves a matplotlib analytics dashboard showing candidate ranking,
    status distribution, and score comparisons.
    """
    if output_image_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_image_path = os.path.join(current_dir, "outputs", "summary_dashboard.png")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

    if df.empty:
        return output_image_path

    # Use a clean non-interactive backend for server/CLI compatibility
    matplotlib.use('Agg')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Color mapping for statuses
    status_colors = {
        "Shortlisted": "#2E7D32",   # Dark Green
        "Under Review": "#F57C00",  # Amber/Orange
        "Rejected": "#D32F2F"       # Crimson Red
    }
    bar_colors = [status_colors.get(s, "#757575") for s in df["Status"]]

    # 1. Bar Chart: Candidate Final Scores
    names = df["Candidate Name"]
    scores = df["Final Score (%)"]
    bars = ax1.barh(names, scores, color=bar_colors, edgecolor="black", height=0.6)
    ax1.set_xlabel("Overall ATS Match Score (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Candidate Rankings & ATS Score Comparison", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlim(0, 105)
    ax1.invert_yaxis()  # Top rank at top
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    # Annotate bar values
    for bar in bars:
        width = bar.get_width()
        ax1.text(width + 1.5, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%",
                 ha='left', va='center', fontsize=9, fontweight='bold', color="#212121")

    # 2. Donut/Pie Chart: Status Distribution
    status_counts = df["Status"].value_counts()
    pie_colors = [status_colors.get(s, "#757575") for s in status_counts.index]

    wedges, texts, autotexts = ax2.pie(
        status_counts.values,
        labels=status_counts.index,
        colors=pie_colors,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        textprops=dict(fontsize=11, fontweight="bold")
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(10)
    ax2.set_title("Hiring Decision Breakdown", fontsize=13, fontweight="bold", pad=12)

    plt.tight_layout()
    plt.savefig(output_image_path, dpi=200, bbox_inches='tight')
    plt.close()

    return output_image_path
