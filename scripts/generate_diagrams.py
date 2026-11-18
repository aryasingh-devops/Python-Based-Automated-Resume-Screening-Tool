"""
Generates high-resolution diagrams and project illustrations for the images/ directory
to ensure the GitHub repository has complete visual documentation.
"""

import os
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_workflow_diagram(output_path):
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.axis('off')

    steps = [
        {"title": "1. Ingestion", "desc": "PDF / DOCX / TXT\nMulti-Format Parsers", "color": "#3B82F6"},
        {"title": "2. Preprocessing", "desc": "Regex Scrubbing\nStopword Filtering", "color": "#10B981"},
        {"title": "3. Skill Extractor", "desc": "Taxonomy Matching\nAlias Resolution", "color": "#F59E0B"},
        {"title": "4. Vectorizer", "desc": "TF-IDF (1,2) N-Grams\nCosine Similarity", "color": "#8B5CF6"},
        {"title": "5. Hybrid Scoring", "desc": "60% Skill + 40% TF-IDF\n+ Preferred Bonus", "color": "#EC4899"},
        {"title": "6. Decision", "desc": "Shortlist / Review / Reject\nCSV & Web Reports", "color": "#06B6D4"}
    ]

    n = len(steps)
    width = 1.6
    height = 2.2
    gap = 0.4
    start_x = 0.5
    y = 2.0

    for i, step in enumerate(steps):
        x = start_x + i * (width + gap)
        # Card
        rect = patches.FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.15,rounding_size=0.15",
            facecolor=step["color"], edgecolor="#1E293B", linewidth=1.5, alpha=0.9
        )
        ax.add_patch(rect)

        # Title
        ax.text(x + width / 2, y + height - 0.45, step["title"],
                ha='center', va='center', color='white', fontsize=11, fontweight='bold')

        # Divider
        ax.plot([x + 0.15, x + width - 0.15], [y + height - 0.8, y + height - 0.8], color='white', lw=1, alpha=0.6)

        # Desc
        ax.text(x + width / 2, y + (height - 0.8) / 2, step["desc"],
                ha='center', va='center', color='white', fontsize=8.5, multialignment='center')

        # Arrow to next
        if i < n - 1:
            arrow = patches.FancyArrowPatch(
                (x + width + 0.05, y + height / 2),
                (x + width + gap - 0.05, y + height / 2),
                arrowstyle='->,head_width=4,head_length=6',
                color='#334155', lw=2.5
            )
            ax.add_patch(arrow)

    ax.set_xlim(0, start_x + n * (width + gap) + 0.2)
    ax.set_ylim(0.8, 5.2)

    plt.title("Automated Resume Screening System - End-to-End Processing Workflow",
              fontsize=14, fontweight='bold', pad=15, color='#0F172A')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Generated: {output_path}")

def setup_images():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "images")
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(images_dir, exist_ok=True)

    # 1. Generate workflow diagram
    workflow_path = os.path.join(images_dir, "workflow_pipeline.png")
    generate_workflow_diagram(workflow_path)

    # 2. Copy summary dashboard to images
    src_chart = os.path.join(outputs_dir, "summary_dashboard.png")
    dst_chart = os.path.join(images_dir, "screening_dashboard.png")
    if os.path.exists(src_chart):
        shutil.copyfile(src_chart, dst_chart)
        print(f"Copied dashboard chart to: {dst_chart}")

if __name__ == "__main__":
    setup_images()
