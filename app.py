"""
Automated Resume Screening Tool - Interactive Streamlit Web Dashboard.
Allows HR recruiters, hiring managers, and candidates to evaluate resumes,
view candidate rankings, inspect skill gaps, and simulate an enterprise ATS.
"""

import os
import json
import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

# Set matplotlib backend for thread safety
matplotlib.use("Agg")

from src.extractor import (
    extract_resume_data,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    extract_contact_info,
    extract_candidate_name
)
from src.matcher import compute_hybrid_score
from src.reporter import generate_candidate_report, assign_decision

# Streamlit Page Config
st.set_page_config(
    page_title="Automated Resume Screening Tool | Enterprise ATS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .status-shortlisted {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-review {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-rejected {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .skill-tag {
        display: inline-block;
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .skill-tag-missing {
        display: inline-block;
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_default_job_descriptions():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "job_descriptions.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def parse_uploaded_file(uploaded_file):
    """Parses in-memory uploaded resume files."""
    fname = uploaded_file.name
    ext = os.path.splitext(fname)[1].lower()
    raw_text = ""

    bytes_data = uploaded_file.read()
    temp_stream = io.BytesIO(bytes_data)

    if ext == ".pdf":
        from pypdf import PdfReader
        try:
            reader = PdfReader(temp_stream)
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    raw_text += txt + "\n"
        except Exception as e:
            st.error(f"Error parsing PDF '{fname}': {e}")
    elif ext in [".docx", ".doc"]:
        from docx import Document
        try:
            doc = Document(temp_stream)
            for p in doc.paragraphs:
                if p.text.strip():
                    raw_text += p.text + "\n"
            for t in doc.tables:
                for row in t.rows:
                    cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if cells:
                        raw_text += " | ".join(cells) + "\n"
        except Exception as e:
            st.error(f"Error parsing Word DOCX '{fname}': {e}")
    elif ext == ".txt":
        try:
            raw_text = bytes_data.decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"Error reading TXT '{fname}': {e}")

    contacts = extract_contact_info(raw_text)
    name = extract_candidate_name(raw_text, fname)

    return {
        "filename": fname,
        "file_type": ext.replace(".", "").upper(),
        "candidate_name": name,
        "email": contacts["email"],
        "phone": contacts["phone"],
        "linkedin": contacts["linkedin"],
        "github": contacts["github"],
        "raw_text": raw_text
    }


# Load Database
job_db = load_default_job_descriptions()

# Sidebar: Job Configuration
st.sidebar.title("⚙️ ATS Configuration")

job_options = list(job_db.keys()) + ["Custom Job Description"]
selected_job_key = st.sidebar.selectbox(
    "Select Target Job Position",
    options=job_options,
    format_func=lambda k: job_db[k]["title"] if k in job_db else "✍️ Enter Custom Position"
)

if selected_job_key in job_db:
    current_job = job_db[selected_job_key]
    job_title = current_job["title"]
    default_req_skills = ", ".join(current_job["required_skills"])
    default_pref_skills = ", ".join(current_job.get("preferred_skills", []))
    default_description = current_job["description"]
else:
    job_title = st.sidebar.text_input("Job Title", value="Software Engineer")
    default_req_skills = "Python, SQL, Git, Docker, REST APIs"
    default_pref_skills = "AWS, CI/CD, Kubernetes"
    default_description = "We are seeking a Software Engineer to design, code, and deploy modern scalable services."

req_skills_input = st.sidebar.text_area(
    "Required Skills (comma-separated)",
    value=default_req_skills,
    height=80
)
pref_skills_input = st.sidebar.text_area(
    "Preferred Skills (comma-separated)",
    value=default_pref_skills,
    height=70
)
job_desc_input = st.sidebar.text_area(
    "Job Description Text",
    value=default_description,
    height=120
)

# Parse Skill lists
required_skills = [s.strip() for s in req_skills_input.split(",") if s.strip()]
preferred_skills = [s.strip() for s in pref_skills_input.split(",") if s.strip()]

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Screening Thresholds")
shortlist_cutoff = st.sidebar.slider("Shortlist Cutoff (%)", min_value=50, max_value=90, value=70, step=5)
review_cutoff = st.sidebar.slider("Review Cutoff (%)", min_value=30, max_value=65, value=50, step=5)

st.sidebar.markdown("---")
source_mode = st.sidebar.radio(
    "Resume Source",
    options=["📂 Pre-loaded Sample Resumes", "📤 Upload Custom Files"]
)

# Main Dashboard Header
st.markdown('<div class="main-title">📄 Automated Resume Screening & ATS System</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-title">Screening candidates against: <b>{job_title}</b> | '
    f'Mandatory Skills: <b>{len(required_skills)}</b> | Preferred Skills: <b>{len(preferred_skills)}</b></div>',
    unsafe_allow_html=True
)

resumes_to_process = []

if source_mode == "📂 Pre-loaded Sample Resumes":
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resumes")
    if os.path.exists(sample_dir):
        files = [f for f in os.listdir(sample_dir) if f.lower().endswith((".pdf", ".docx", ".txt"))]
        for f in files:
            path = os.path.join(sample_dir, f)
            resumes_to_process.append(extract_resume_data(path))
else:
    uploaded_files = st.file_uploader(
        "Upload Candidate Resumes (PDF, DOCX, TXT supported)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for uf in uploaded_files:
            resumes_to_process.append(parse_uploaded_file(uf))

if not resumes_to_process:
    st.info("ℹ️ No resumes loaded. Choose 'Pre-loaded Sample Resumes' or upload your own files to begin screening.")
    st.stop()

# Evaluate All Resumes
evaluations = []
for res in resumes_to_process:
    score_data = compute_hybrid_score(
        resume_text=res["raw_text"],
        jd_text=job_desc_input,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        job_title=job_title
    )
    combined = {**res, **score_data}
    evaluations.append(combined)

# Generate Tabular Report
df_report = generate_candidate_report(
    evaluations,
    shortlist_threshold=shortlist_cutoff,
    review_threshold=review_cutoff
)

# Top KPI Metric Cards
total_cands = len(df_report)
shortlisted_cands = len(df_report[df_report["Status"] == "Shortlisted"])
review_cands = len(df_report[df_report["Status"] == "Under Review"])
rejected_cands = len(df_report[df_report["Status"] == "Rejected"])
top_score = df_report["Final Score (%)"].max() if not df_report.empty else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Applicants", f"{total_cands}")
col2.metric("✅ Shortlisted", f"{shortlisted_cands}", delta=f"{shortlisted_cands/total_cands*100:.0f}%")
col3.metric("⚠️ Under Review", f"{review_cands}")
col4.metric("❌ Rejected", f"{rejected_cands}")
col5.metric("🏆 Top Score", f"{top_score:.1f}%")

st.markdown("---")

# Main Content Tabs
tab_leaderboard, tab_inspector, tab_live_test, tab_guide = st.tabs([
    "📊 Candidate Leaderboard",
    "🔍 Deep Candidate Inspector",
    "⚡ Live Resume Tester",
    "📚 ATS Architecture & Guide"
])

# ----------------- TAB 1: LEADERBOARD -----------------
with tab_leaderboard:
    st.subheader("Candidate Rankings & ATS Scores")

    # Filter by Status
    status_filter = st.multiselect(
        "Filter by Status",
        options=["Shortlisted", "Under Review", "Rejected"],
        default=["Shortlisted", "Under Review", "Rejected"]
    )

    filtered_df = df_report[df_report["Status"].isin(status_filter)]

    # Styled Table
    def highlight_status(val):
        if val == "Shortlisted":
            return "background-color: #DCFCE7; color: #166534; font-weight: bold;"
        elif val == "Under Review":
            return "background-color: #FEF3C7; color: #92400E; font-weight: bold;"
        elif val == "Rejected":
            return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
        return ""

    styler = filtered_df.style
    if hasattr(styler, "map"):
        styled_df = styler.map(highlight_status, subset=["Status"])
    else:
        styled_df = styler.applymap(highlight_status, subset=["Status"])

    styled_df = styled_df.format({
        "Final Score (%)": "{:.1f}%",
        "Skill Match (%)": "{:.1f}%",
        "TF-IDF Match (%)": "{:.1f}%"
    })

    st.dataframe(styled_df, use_container_width=True)

    # Download CSV Button
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Screening Report (CSV)",
        data=csv_bytes,
        file_name="ats_screening_report.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("Visual Analytics")
    c1, c2 = st.columns([3, 2])

    with c1:
        # Candidate Score Horizontal Bar Chart
        fig_bar, ax_bar = plt.subplots(figsize=(8, 4.5))
        status_palette = {"Shortlisted": "#2E7D32", "Under Review": "#F57C00", "Rejected": "#D32F2F"}
        colors_list = [status_palette.get(s, "#757575") for s in filtered_df["Status"]]

        bars = ax_bar.barh(filtered_df["Candidate Name"], filtered_df["Final Score (%)"], color=colors_list, height=0.55)
        ax_bar.set_xlabel("Overall ATS Match Score (%)", fontweight="bold")
        ax_bar.set_title("Candidate Rankings vs. Thresholds", fontweight="bold", pad=10)
        ax_bar.set_xlim(0, 105)
        ax_bar.invert_yaxis()
        ax_bar.axvline(shortlist_cutoff, color='#2E7D32', linestyle='--', label=f'Shortlist ({shortlist_cutoff}%)')
        ax_bar.axvline(review_cutoff, color='#F57C00', linestyle=':', label=f'Review ({review_cutoff}%)')
        ax_bar.legend(loc='lower right')
        ax_bar.grid(axis='x', linestyle='--', alpha=0.4)

        for bar in bars:
            w = bar.get_width()
            ax_bar.text(w + 1.2, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%",
                        va='center', fontsize=8.5, fontweight='bold')

        st.pyplot(fig_bar)
        plt.close(fig_bar)

    with c2:
        # Donut Chart for Status Ratio
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4.5))
        counts = df_report["Status"].value_counts()
        pie_colors = [status_palette.get(s, "#757575") for s in counts.index]

        ax_pie.pie(
            counts.values,
            labels=counts.index,
            colors=pie_colors,
            autopct='%1.1f%%',
            startangle=140,
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
            textprops=dict(fontsize=10, fontweight="bold")
        )
        ax_pie.set_title("Hiring Pipeline Breakdown", fontweight="bold", pad=10)
        st.pyplot(fig_pie)
        plt.close(fig_pie)

# ----------------- TAB 2: DEEP CANDIDATE INSPECTOR -----------------
with tab_inspector:
    st.subheader("Detailed Candidate Profile & Skill Gap Analysis")

    cand_names = [e["candidate_name"] for e in evaluations]
    selected_name = st.selectbox("Select Candidate to Inspect", options=cand_names)

    selected_cand = next((e for e in evaluations if e["candidate_name"] == selected_name), None)

    if selected_cand:
        c_left, c_right = st.columns([1, 2])

        with c_left:
            st.markdown(f"### {selected_cand['candidate_name']}")
            status_val = assign_decision(selected_cand['final_score'], shortlist_cutoff, review_cutoff)

            if status_val == "Shortlisted":
                st.markdown('<span class="status-shortlisted">✅ Shortlisted</span>', unsafe_allow_html=True)
            elif status_val == "Under Review":
                st.markdown('<span class="status-review">⚠️ Under Review</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-rejected">❌ Rejected</span>', unsafe_allow_html=True)

            st.write("")
            st.write(f"📧 **Email:** {selected_cand.get('email') or 'Not Detected'}")
            st.write(f"📞 **Phone:** {selected_cand.get('phone') or 'Not Detected'}")
            if selected_cand.get('github'):
                st.write(f"🐙 **GitHub:** [{selected_cand['github']}](https://{selected_cand['github']})")
            if selected_cand.get('linkedin'):
                st.write(f"💼 **LinkedIn:** [{selected_cand['linkedin']}](https://{selected_cand['linkedin']})")

            st.markdown("---")
            st.write("**ATS Score Breakdown:**")
            st.metric("Overall Match Score", f"{selected_cand['final_score']}%")
            st.metric("Skill Match Score (60% wt)", f"{selected_cand['skill_score']}%")
            st.metric("TF-IDF Semantic Match (40% wt)", f"{selected_cand['tfidf_score']}%")
            if selected_cand.get("preferred_bonus", 0) > 0:
                st.metric("Preferred Skills Bonus", f"+{selected_cand['preferred_bonus']}%")

        with c_right:
            st.write("#### 🎯 Required Skills Evaluation")
            matched_req = selected_cand.get("matched_required_skills", [])
            missing_req = selected_cand.get("missing_required_skills", [])

            st.write(f"**Matched Skills ({len(matched_req)}/{len(required_skills)}):**")
            if matched_req:
                tags_html = "".join([f'<span class="skill-tag">✓ {s}</span>' for s in matched_req])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.write("None matched.")

            st.write("")
            st.write(f"**Missing Skills ({len(missing_req)}):**")
            if missing_req:
                tags_missing_html = "".join([f'<span class="skill-tag-missing">✕ {s}</span>' for s in missing_req])
                st.markdown(tags_missing_html, unsafe_allow_html=True)
            else:
                st.success("All required skills are present on this resume!")

            st.markdown("---")
            st.write("#### 🗂️ All Extracted Technical Skills (By Category)")
            cat_skills = selected_cand.get("categorized_skills", {})
            if cat_skills:
                for cat, sk_list in cat_skills.items():
                    clean_cat = cat.replace("_", " ").title()
                    st.write(f"**{clean_cat}:** {', '.join(sk_list)}")
            else:
                st.write("No recognized technical skills found.")

            with st.expander("📄 View Extracted Raw Text"):
                st.text_area("Resume Raw Text", value=selected_cand.get("raw_text", ""), height=220)

# ----------------- TAB 3: LIVE RESUME TESTER -----------------
with tab_live_test:
    st.subheader("⚡ Live Resume ATS Optimizer")
    st.write("Paste your own resume text below to test how it scores against the selected Job Description in real-time.")

    col_paste, col_result = st.columns([1, 1])

    with col_paste:
        user_pasted_resume = st.text_area(
            "Paste Resume Text Here",
            height=300,
            placeholder="Paste your resume content (Summary, Experience, Skills, Education)..."
        )
        test_btn = st.button("🚀 Analyze & Score Resume")

    with col_result:
        if test_btn and user_pasted_resume.strip():
            live_result = compute_hybrid_score(
                resume_text=user_pasted_resume,
                jd_text=job_desc_input,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                job_title=job_title
            )

            st.markdown("### Match Results")
            st.progress(live_result["final_score"] / 100)
            st.metric("Overall ATS Score", f"{live_result['final_score']}%")

            st.write(f"**Skill Match:** {live_result['skill_score']}%")
            st.write(f"**TF-IDF Semantic Similarity:** {live_result['tfidf_score']}%")

            st.write("#### 💡 How to Improve Your Score:")
            if live_result["missing_required_skills"]:
                st.warning(f"Add evidence or mention of missing keywords: {', '.join(live_result['missing_required_skills'])}")
            else:
                st.success("Great job! You have covered all mandatory skills for this role.")
        elif test_btn:
            st.warning("Please paste some resume text first.")

# ----------------- TAB 4: ARCHITECTURE & GUIDE -----------------
with tab_guide:
    st.subheader("🏛️ System Architecture & ATS Mechanics")
    st.markdown("""
    ### How Does This ATS Work?

    Modern Applicant Tracking Systems (ATS) combine **Rule-Based Skill Extraction** with **Statistical Natural Language Processing (NLP)**.

    #### 1. Processing Pipeline
    1. **Document Ingestion**: Extracts text from `.pdf`, `.docx`, and `.txt` files using `pypdf` and `python-docx`.
    2. **NLP Text Cleaning**: Strips noisy symbols, email headers, URLs, and English stop words while preserving tech tokens (`C++`, `C#`, `.NET`, `CI/CD`).
    3. **Skill Taxonomy Extraction**: Searches for over 200+ industry-standard skills grouped into categories (Languages, Frameworks, Cloud, Databases).
    4. **TF-IDF & Cosine Similarity**: Uses Scikit-learn's `TfidfVectorizer` (with 1-gram and 2-gram phrases) to convert resumes and job descriptions into high-dimensional vector spaces and computes cosine angle similarity.
    5. **Hybrid ATS Scoring**:
    """)
    st.latex(r"\text{Final ATS Score} = (0.60 \times \text{Skill Overlap \%}) + (0.40 \times \text{TF-IDF Cosine Similarity \%}) + \text{Bonus}")
    st.markdown("""
    #### 2. Why Combine TF-IDF and Skill Matching?
    - **Skill Matching Alone** is vulnerable to missing contextual depth and candidate projects.
    - **TF-IDF Alone** can dilute the importance of non-negotiable core skills (e.g. knowing Python for a Python backend role).
    - **The Hybrid Engine** mirrors commercial systems like Workday, Lever, and Greenhouse by enforcing strict skill prerequisites while rewarding deep technical domain alignment.
    """)
