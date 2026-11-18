# System Architecture: Automated Resume Screening Tool

## 1. High-Level Architecture Overview

The **Automated Resume Screening Tool** is designed as a modular Natural Language Processing (NLP) pipeline that bridges the gap between unstructured document formats (PDF, Word, Text) and structured candidate evaluation.

```
+-----------------------------------------------------------------------------------+
|                               INPUT LAYER                                         |
|  +--------------------+   +-----------------------+   +------------------------+  |
|  | Multi-Format       |   | Target Job Position   |   | Mandatory & Preferred  |  |
|  | Resumes (.pdf/.docx|   | Corporate Description |   | Skill Sets             |  |
|  +--------------------+   +-----------------------+   +------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             EXTRACTION & PARSING                                  |
|  +-----------------------------+         +-------------------------------------+  |
|  | Document Readers            |         | Metadata & Contact Extractor        |  |
|  | (pypdf, python-docx)        |         | (Regex: Name, Email, Phone, Social) |  |
|  +-----------------------------+         +-------------------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             NLP PREPROCESSING LAYER                               |
|  +-----------------------------------------------------------------------------+  |
|  | • URL & Hyperlink Stripping                                                 |  |
|  | • Special Symbol Preservation (C++, C#, .NET, CI/CD normalization)          |  |
|  | • Custom NLP Stopwords Filtering                                            |  |
|  | • Lowercasing & Token Regularization                                        |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             EVALUATION & SCORING ENGINE                           |
|  +-------------------------------+             +-------------------------------+  |
|  | Skill Taxonomy Matcher        |             | TF-IDF Semantic Engine        |  |
|  | • Acronym & Alias Mapping     |             | • (1, 2) N-Gram Vectorization |  |
|  | • Exact Boundary Regex        |             | • Cosine Angle Similarity     |  |
|  | • Skill Match % (60% Weight)  |             | • Semantic Match % (40% Weight|  |
|  +-------------------------------+             +-------------------------------+  |
|                                  \             /                                  |
|                                   \           /                                   |
|                                    v         v                                    |
|                   +---------------------------------------+                       |
|                   | Hybrid ATS Scoring Engine             |                       |
|                   | Score = (0.60 * Skill) + (0.40 * TF)  |                       |
|                   |         + Preferred Bonus (+5%)       |                       |
|                   +---------------------------------------+                       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             DECISION & REPORTING LAYER                            |
|  +------------------------+  +--------------------------+  +-------------------+  |
|  | Threshold Classifier   |  | CSV & Visual Analytics   |  | Streamlit Web UI  |  |
|  | >= 70%: Shortlisted    |  | • screening_report.csv   |  | Interactive App   |  |
|  | 50-69%: Under Review   |  | • summary_dashboard.png  |  | Live Optimizer    |  |
|  | < 50%: Rejected        |  |                          |  |                   |  |
|  +------------------------+  +--------------------------+  +-------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Modules & Responsibilities

| Module | File | Purpose |
|---|---|---|
| **Text Extractor** | `src/extractor.py` | Ingests `.pdf`, `.docx`, and `.txt` files; extracts candidate name, email, phone, and links. |
| **Text Cleaner** | `src/cleaner.py` | Sanitizes raw text, removes English stopwords, normalizes developer tech tokens. |
| **Skill Extractor** | `src/skill_extractor.py` | Maps 200+ skills across 7 categories; handles aliases like `restful apis` / `rest`, `sklearn` / `scikit-learn`. |
| **Scoring Engine** | `src/matcher.py` | Generates TF-IDF matrices with unigram/bigram n-grams, computes Cosine Similarity, and applies hybrid weighting. |
| **Reporter** | `src/reporter.py` | Assigns shortlist/review/reject verdicts, formats Pandas DataFrames, and exports CSV and charts. |
| **Interactive App** | `app.py` | Rich Streamlit browser application with live file upload, threshold sliders, candidate radar, and optimizer. |
| **CLI Runner** | `main.py` | Batch command-line pipeline for scheduled or terminal-based screening runs. |

---

## 3. Mathematical Foundations of Scoring

### A. TF-IDF (Term Frequency - Inverse Document Frequency)
$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t', d}}$$

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

### B. Cosine Similarity
$$\text{Cosine Similarity}(\vec{A}, \vec{B}) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} = \frac{\sum_{i=1}^n A_i B_i}{\sqrt{\sum_{i=1}^n A_i^2} \sqrt{\sum_{i=1}^n B_i^2}}$$

### C. Hybrid ATS Score
$$\text{Score}_{\text{ATS}} = \min\left(100.0, \; \left(w_{\text{skill}} \times S_{\text{skill}}\right) + \left(w_{\text{tfidf}} \times S_{\text{tfidf}}\right) + B_{\text{preferred}}\right)$$
Where:
- $w_{\text{skill}} = 0.60$ (Skill weight)
- $w_{\text{tfidf}} = 0.40$ (TF-IDF weight)
- $B_{\text{preferred}} \le 5.0$ (Bonus points for nice-to-have capabilities)
