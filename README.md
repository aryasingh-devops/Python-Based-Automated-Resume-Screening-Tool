# 📄 Automated Resume Screening Tool (Enterprise ATS)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework-Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Scikit--Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![License-MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An industry-grade **Automated Resume Screening Tool and Applicant Tracking System (ATS)** built in Python. It parses multi-format resumes (`.pdf`, `.docx`, `.txt`), performs NLP cleaning, extracts technical skill taxonomies, calculates semantic TF-IDF cosine similarities, ranks candidates, and generates actionable hiring reports.

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement & Industry Relevance](#-problem-statement--industry-relevance)
3. [Key Features](#-key-features)
4. [Tech Stack](#-tech-stack)
5. [System Architecture](#-system-architecture)
6. [Folder Structure](#-folder-structure)
7. [Installation & Setup](#-installation--setup)
8. [How to Run the Project](#-how-to-run-the-project)
9. [Virtual Simulation Guide](#-virtual-simulation-guide)
10. [Sample Output & Results](#-sample-output--results)
11. [Interview Preparation](#-interview-preparation)
12. [License](#-license)

---

## 🌟 Project Overview

When corporate job openings receive hundreds of applicants within days, human recruiters face an impossible bottleneck. This project simulates an **Enterprise ATS Engine** (similar to Workday, Greenhouse, or Lever) that automates candidate shortlisting using a **Hybrid Scoring Model**:
- **60% Skill Match:** Enforces mandatory technical prerequisites with alias mapping.
- **40% TF-IDF Cosine Similarity:** Evaluates semantic depth, project descriptions, and domain terminology across unigram and bigram tokens.
- **Preferred Skill Bonus:** Rewards supplementary competencies (up to +5%).

## 📸 Output Screenshots

<img width="1920" height="1020" alt="Screenshot 2026-11-18 230237" src="https://github.com/user-attachments/assets/ab32241c-8db5-4d1e-a536-03e5f21a093e" />
<img width="1920" height="1020" alt="Screenshot 2026-11-18 231125" src="https://github.com/user-attachments/assets/69d1dd78-39f5-4a0d-ac7e-d2dd6b994717" />
<img width="1920" height="1020" alt="Screenshot 2026-11-18 231137" src="https://github.com/user-attachments/assets/7442d3cb-e02c-4aa7-8ad4-66753472a69b" />

## 🎥 Demo Video

https://youtu.be/ij2z1LZ1Obk?si=IYIlTTot57la0nu9

---

## 💼 Problem Statement & Industry Relevance

| Challenge in Traditional Hiring | How This Tool Solves It |
|---|---|
| **Resume Overload:** Over 250+ resumes per job post. | Batch screens dozens of resumes in seconds. |
| **Keyword Stuffing:** Candidates spamming keywords without real substance. | Hybrid scoring balances exact keywords with contextual TF-IDF domain similarity. |
| **Incompatible File Types:** Parsing fails across PDFs, Word docs, and plain text. | Multi-engine parser using `pypdf` and `python-docx`. |
| **Lack of Transparency:** Opaque rejection decisions. | Generates candidate-specific skill gap reports (Matched vs Missing skills). |
| **Unconscious Bias:** Screening influenced by demographics. | PII (name, gender, location) is extracted for contact only and excluded from scoring vectors. |

---

## 🚀 Key Features

- **Multi-Format Parsing:** Ingests `.pdf`, `.docx`, `.doc`, and `.txt` resumes.
- **Automated Contact Extraction:** Regular expression extraction of email addresses, phone numbers, GitHub, and LinkedIn profiles.
- **Intelligent Skill Taxonomy:** 200+ technology skills cataloged across 7 categories with acronym and alias expansion (`scikit-learn` / `sklearn`, `ci/cd` / `continuous integration`, `restful apis` / `rest`).
- **Hybrid ATS Scoring Algorithm:** Combines keyword overlap with TF-IDF cosine angle similarity.
- **Interactive Web App (Streamlit):**
  - Switch target roles or input custom Job Descriptions.
  - Interactive candidate leaderboard with sorting and filtering.
  - Deep candidate inspector showing skill badges (matched vs missing).
  - Live Resume Optimizer: paste resume text and receive immediate feedback.
- **Headless CLI Pipeline:** Process directories and generate CSV reports from the terminal.
- **Exportable Reports:** Ranked CSV spreadsheets and publication-ready matplotlib visual charts.

---

## 🛠️ Tech Stack

- **Core Language:** Python 3.10+
- **Data Manipulation:** `pandas`, `numpy`
- **Machine Learning & NLP:** `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`), `re` (Regex)
- **Document Processing:** `pypdf`, `python-docx`, `reportlab`
- **Web UI & Dashboard:** `streamlit`
- **Visualization:** `matplotlib`, `seaborn`

---

## 🏛️ System Architecture

```
+---------------------------------------------------------------------------------+
|                                 INPUT LAYER                                     |
|     Resumes (.pdf / .docx)    +    Job Description    +    Required Skills      |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                         PARSING & NLP CLEANING LAYER                            |
|       Text Extraction  -->  Regex Stripping  -->  Stopword Normalization        |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                              EVALUATION ENGINE                                  |
|   +-------------------------------+         +-------------------------------+   |
|   |   Skill Overlap Percentage    |         |   TF-IDF Cosine Similarity    |   |
|   |         (60% Weight)          |         |         (40% Weight)          |   |
|   +-------------------------------+         +-------------------------------+   |
|                                   \         /                                   |
|                                    v       v                                    |
|              Final ATS Score = (0.60 * Skill) + (0.40 * TFIDF) + Bonus          |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                             OUTPUT & DECISION LAYER                             |
|    • Shortlisted (>= 70%)     • Under Review (50-69%)     • Rejected (< 50%)    |
|    • CSV Export               • Analytics Chart           • Streamlit Dashboard |
+---------------------------------------------------------------------------------+
```

---

## 📂 Folder Structure

```
Python-Automated Resume Screening Tool/
│
├── resumes/                      # Sample synthetic resumes (PDF & DOCX)
│   ├── alex_turner_senior_python_dev.pdf
│   ├── priya_sharma_data_scientist.pdf
│   ├── marcus_chen_backend_engineer.docx
│   ├── sophia_rodriguez_data_analyst.pdf
│   ├── david_kim_frontend_react.docx
│   ├── elena_rostova_digital_marketer.pdf
│   ├── rohit_verma_junior_python.pdf
│   └── chloe_dupont_graphic_designer.docx
│
├── data/                         # Knowledge base & predefined roles
│   ├── job_descriptions.json     # Pre-configured corporate job specs
│   └── skills_dictionary.json    # 200+ categorized skill taxonomies
│
├── src/                          # Modular core engine
│   ├── __init__.py
│   ├── extractor.py              # PDF, DOCX, TXT text & contact extractor
│   ├── cleaner.py                # Regex cleaner & stopword filtering
│   ├── skill_extractor.py        # Skill taxonomy & alias matcher
│   ├── matcher.py                # TF-IDF vectorizer & hybrid ATS scorer
│   └── reporter.py               # DataFrame generator, CSV export & plotting
│
├── outputs/                      # Generated evaluation artifacts
│   ├── screening_report.csv      # Ranked candidate spreadsheet
│   └── summary_dashboard.png     # Visual analytics dashboard chart
│
├── scripts/                      # Utility scripts
│   └── generate_sample_resumes.py# Programmatic resume creator (ReportLab & docx)
│
├── docs/                         # Documentation & interview preparation
│   ├── ARCHITECTURE.md           # In-depth system design & mathematical formulas
│   └── INTERVIEW_QA.md           # HR Tech, NLP, and Python technical Q&A
│
├── app.py                        # Interactive Streamlit browser web app
├── main.py                       # Standalone CLI batch screening pipeline
├── requirements.txt              # Project dependencies
├── .gitignore                    # Git tracking ignore rules
└── README.md                     # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Automated-Resume-Screening-Tool.git
cd Automated-Resume-Screening-Tool
```

### 2. Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Project

### Option A: Interactive Browser Dashboard (Streamlit)
Launch the interactive web interface in your browser:
```bash
streamlit run app.py
```
- Open `http://localhost:8501` in your browser.
- Select target job positions, adjust thresholds, inspect candidate skill gaps, and paste your own resume.

### Option B: Command Line Interface (CLI)
Run batch screening from the terminal against pre-configured positions:

```bash
# 1. Screen candidates for Python Backend Developer
python main.py --job python_backend_developer

# 2. Screen candidates for Data Scientist
python main.py --job data_scientist

# 3. Screen candidates for Data Analyst
python main.py --job data_analyst

# 4. Custom thresholds (e.g. 75% for Shortlist, 55% for Review)
python main.py --job python_backend_developer --shortlist 75 --review 55
```

---

## 🧪 Virtual Simulation Guide

To simulate a real HR corporate recruitment campaign:
1. **Generate Synthetic Resumes:** Run `python scripts/generate_sample_resumes.py` to create 8 multi-domain resumes in PDF and DOCX formats.
2. **Execute Screening:** Run `python main.py --job python_backend_developer`.
3. **Inspect Output Files:**
   - Open `outputs/screening_report.csv` in Excel to view candidate rankings and contact info.
   - Open `outputs/summary_dashboard.png` to review the score distribution visual chart.
4. **Interactive Audit:** Launch `streamlit run app.py` to explore the candidate profile inspector and test custom resumes in the Live Optimizer.

---

## 📊 Sample Output & Results

### Terminal Screening Output (Python Backend Developer Position)

```
======================================================================
      AUTOMATED RESUME SCREENING & ATS EVALUATION SYSTEM
======================================================================

[Target Position] : Senior Python Backend Developer (Core Engineering)
[Experience Need] : 3-5 years
[Required Skills] : Python, Django, FastAPI, PostgreSQL, Docker, RESTful APIs, Git, Redis, Linux, CI/CD
[Preferred Skills]: AWS, Kubernetes, Microservices Architecture, Celery, PyTest
----------------------------------------------------------------------

[Scanning] Found 8 resumes in 'resumes/'
  -> [1/8] Processed: Alex Turner (alex_turner_senior_python_dev.pdf) - Score: 80.09%
  -> [2/8] Processed: Marcus Chen (marcus_chen_backend_engineer.docx) - Score: 48.48%
  -> [3/8] Processed: Priya Sharma (priya_sharma_data_scientist.pdf) - Score: 25.73%
  ...

======================================================================
                    FINAL SCREENING RANKINGS
======================================================================
 Rank   Candidate Name       Status  Final Score (%)  Skill Match (%)  TF-IDF Match (%)
    1      Alex Turner  Shortlisted            80.09           100.00             37.73
    2      Marcus Chen Under Review            48.48            70.00             13.69
    3     Priya Sharma     Rejected            25.73            40.00              4.32
    4      Rohit Verma     Rejected            20.56            30.00              6.39
    5 Sophia Rodriguez     Rejected            14.06            20.00              5.14
    6        David Kim     Rejected            13.18            20.00              2.96
    7     Chloe Dupont     Rejected             0.68             0.00              1.71
    8    Elena Rostova     Rejected             0.14             0.00              0.35

----------------------------------------------------------------------
DECISION SUMMARY : Shortlisted: 1 | Under Review: 1 | Rejected: 6
----------------------------------------------------------------------
```

---

## 🎓 Interview Preparation & Concepts

Use the accompanying [Technical Interview Preparation Guide](docs/INTERVIEW_QA.md) for in-depth discussion points on:
- **TF-IDF vs. Deep Learning (BERT/SBERT):** When to prioritize speed and explainability over dense embeddings.
- **Cosine Similarity vs. Euclidean Distance:** Why document-length normalization is critical for fair resume comparisons.
- **System Design & Bias Mitigation:** How PII masking prevents algorithmic discrimination.

---

## 📄 License

This project is licensed under the MIT License - feel free to use it for educational purposes, portfolio showcases, and recruitment automation experiments.
