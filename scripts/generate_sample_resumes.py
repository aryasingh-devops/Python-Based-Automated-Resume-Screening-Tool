"""
Script to generate realistic synthetic resumes in PDF and DOCX formats.
Used for testing and simulating an ATS (Applicant Tracking System).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from docx import Document
from docx.shared import Pt, Inches, RGBColor

def create_pdf_resume(file_path, name, title, contact, summary, skills, experience, education, projects):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=4
    )
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=8
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#2C5282'),
        spaceBefore=8,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )

    story = []
    story.append(Paragraph(name, header_style))
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(contact, contact_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=8))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 6))

    # Skills
    story.append(Paragraph("TECHNICAL & PROFESSIONAL SKILLS", section_heading))
    story.append(Paragraph(f"<b>Key Skills:</b> {', '.join(skills)}", body_style))
    story.append(Spacer(1, 6))

    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_heading))
    for exp in experience:
        story.append(Paragraph(f"<b>{exp['role']}</b> | <i>{exp['company']}</i> ({exp['period']})", body_style))
        for bullet in exp['bullets']:
            story.append(Paragraph(f"• {bullet}", body_style))
        story.append(Spacer(1, 4))

    # Projects
    if projects:
        story.append(Paragraph("KEY PROJECTS", section_heading))
        for proj in projects:
            story.append(Paragraph(f"<b>{proj['title']}</b> - <i>{proj['tech']}</i>", body_style))
            story.append(Paragraph(f"• {proj['description']}", body_style))
            story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION", section_heading))
    for edu in education:
        story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['institution']} ({edu['year']})", body_style))

    doc.build(story)


def create_docx_resume(file_path, name, title, contact, summary, skills, experience, education, projects):
    doc = Document()
    
    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    # Header
    name_p = doc.add_paragraph()
    name_run = name_p.add_run(name)
    name_run.font.size = Pt(20)
    name_run.font.bold = True
    name_run.font.color.rgb = RGBColor(26, 54, 93)
    name_p.paragraph_format.space_after = Pt(2)

    title_p = doc.add_paragraph()
    title_run = title_p.add_run(title)
    title_run.font.size = Pt(12)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(43, 108, 176)
    title_p.paragraph_format.space_after = Pt(2)

    contact_p = doc.add_paragraph()
    contact_run = contact_p.add_run(contact)
    contact_run.font.size = Pt(9.5)
    contact_run.font.color.rgb = RGBColor(74, 85, 104)
    contact_p.paragraph_format.space_after = Pt(8)

    def add_section_heading(text):
        h = doc.add_paragraph()
        run = h.add_run(text.upper())
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(44, 82, 130)
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(4)

    # Summary
    add_section_heading("Professional Summary")
    p = doc.add_paragraph(summary)
    p.paragraph_format.space_after = Pt(6)

    # Skills
    add_section_heading("Technical & Professional Skills")
    p = doc.add_paragraph()
    r_bold = p.add_run("Key Skills: ")
    r_bold.bold = True
    p.add_run(", ".join(skills))
    p.paragraph_format.space_after = Pt(6)

    # Experience
    add_section_heading("Work Experience")
    for exp in experience:
        ep = doc.add_paragraph()
        r = ep.add_run(f"{exp['role']} | {exp['company']} ({exp['period']})")
        r.bold = True
        ep.paragraph_format.space_after = Pt(2)
        for bullet in exp['bullets']:
            bp = doc.add_paragraph(f"• {bullet}")
            bp.paragraph_format.space_after = Pt(2)

    # Projects
    if projects:
        add_section_heading("Key Projects")
        for proj in projects:
            pp = doc.add_paragraph()
            r1 = pp.add_run(f"{proj['title']} - {proj['tech']}")
            r1.bold = True
            pp.paragraph_format.space_after = Pt(2)
            bp = doc.add_paragraph(f"• {proj['description']}")
            bp.paragraph_format.space_after = Pt(2)

    # Education
    add_section_heading("Education")
    for edu in education:
        edp = doc.add_paragraph()
        r = edp.add_run(f"{edu['degree']} - {edu['institution']} ({edu['year']})")
        r.bold = True
        edp.paragraph_format.space_after = Pt(2)

    doc.save(file_path)


def generate_all_resumes(target_dir):
    os.makedirs(target_dir, exist_ok=True)

    candidates = [
        {
            "format": "pdf",
            "filename": "alex_turner_senior_python_dev.pdf",
            "name": "Alex Turner",
            "title": "Senior Python Backend Developer",
            "contact": "alex.turner@email.com | +1 (555) 234-5678 | San Francisco, CA | github.com/alexturner | linkedin.com/in/alexturner",
            "summary": "Results-driven Senior Python Developer with 5+ years building scalable REST APIs, microservices, and asynchronous distributed systems. Proficient in Python, Django, FastAPI, PostgreSQL, Docker, AWS, Redis, and CI/CD pipelines.",
            "skills": ["Python", "Django", "FastAPI", "Flask", "RESTful APIs", "PostgreSQL", "Redis", "Docker", "AWS", "Kubernetes", "Git", "CI/CD", "Linux", "PyTest", "Celery", "Microservices Architecture"],
            "experience": [
                {
                    "role": "Senior Software Engineer (Python)",
                    "company": "CloudPeak Technologies",
                    "period": "2022 - Present",
                    "bullets": [
                        "Architected scalable microservices backend using FastAPI and PostgreSQL handling 15M daily requests.",
                        "Optimized database queries and implemented Redis caching, reducing API response latency by 45%.",
                        "Containerized backend applications using Docker and orchestrated deployments on AWS ECS."
                    ]
                },
                {
                    "role": "Python Backend Developer",
                    "company": "Nexus Web Solutions",
                    "period": "2019 - 2022",
                    "bullets": [
                        "Developed REST APIs using Django REST framework and integrated third-party payment gateways.",
                        "Implemented asynchronous background task queues with Celery and RabbitMQ.",
                        "Maintained 90%+ code coverage using PyTest and integrated automated GitHub Actions CI/CD workflows."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Distributed Task Scheduler",
                    "tech": "Python, Redis, FastAPI, Docker",
                    "description": "Engineered an asynchronous task execution engine with distributed lock mechanisms and failure retries."
                }
            ],
            "education": [
                {"degree": "B.S. in Computer Science", "institution": "University of California, Berkeley", "year": "2019"}
            ]
        },
        {
            "format": "pdf",
            "filename": "priya_sharma_data_scientist.pdf",
            "name": "Priya Sharma",
            "title": "Data Scientist & Machine Learning Specialist",
            "contact": "priya.sharma@email.com | +1 (555) 456-7890 | Boston, MA | github.com/priyasharma | linkedin.com/in/priyasharma",
            "summary": "Data Scientist with 4 years of experience applying Machine Learning, Natural Language Processing (NLP), and statistical modeling to solve business problems. Expert in Python, Scikit-learn, Pandas, PyTorch, SQL, TF-IDF, and data visualization.",
            "skills": ["Python", "Machine Learning", "NLP", "Pandas", "NumPy", "Scikit-Learn", "PyTorch", "TensorFlow", "SQL", "Tableau", "TF-IDF", "Deep Learning", "Data Cleaning", "Git", "Statistics", "Data Visualization"],
            "experience": [
                {
                    "role": "Lead Data Scientist",
                    "company": "Alpha Analytics Lab",
                    "period": "2021 - Present",
                    "bullets": [
                        "Built NLP sentiment analysis and recommendation pipelines reaching 92% classification accuracy.",
                        "Processed, cleaned, and analyzed 10TB+ relational database records using SQL, Pandas, and NumPy.",
                        "Deployed predictive ML models into production via FastAPI endpoints and Docker containers."
                    ]
                },
                {
                    "role": "Data Analyst / Junior Data Scientist",
                    "company": "MetricBridge Corp",
                    "period": "2020 - 2021",
                    "bullets": [
                        "Created automated ETL pipelines in Python and SQL to power executive business intelligence dashboards.",
                        "Performed feature engineering and exploratory data analysis (EDA) using Matplotlib and Seaborn."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Resume Keyword & Semantic Parser",
                    "tech": "Python, NLP, Scikit-learn, TF-IDF, NLTK",
                    "description": "Developed cosine similarity engine matching candidate profiles to job specifications with ranking metrics."
                }
            ],
            "education": [
                {"degree": "M.S. in Data Analytics", "institution": "Northeastern University", "year": "2020"},
                {"degree": "B.Tech in Computer Science", "institution": "Anna University", "year": "2018"}
            ]
        },
        {
            "format": "docx",
            "filename": "marcus_chen_backend_engineer.docx",
            "name": "Marcus Chen",
            "title": "Full Stack & Backend Python Engineer",
            "contact": "marcus.chen@email.com | +1 (555) 789-0123 | Seattle, WA | github.com/marcuschen | linkedin.com/in/marcuschen",
            "summary": "Full Stack Python Developer with 3+ years experience building web applications using Flask, Django, React, MySQL, and Docker. Strong understanding of RESTful API design, database normalization, and automated unit testing.",
            "skills": ["Python", "Flask", "Django", "JavaScript", "React", "MySQL", "REST APIs", "Git", "Docker", "HTML5", "CSS3", "Linux", "PyTest", "Postman", "Agile"],
            "experience": [
                {
                    "role": "Software Developer",
                    "company": "InnoSoft Systems",
                    "period": "2021 - Present",
                    "bullets": [
                        "Built backend services with Python Flask and MySQL, powering customer-facing portals.",
                        "Collaborated with frontend React developers to deliver secure JWT-authenticated endpoints.",
                        "Wrote unit and integration tests using PyTest to ensure software quality."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "E-Commerce Inventory API",
                    "tech": "Python, Django, PostgreSQL, Swagger",
                    "description": "Implemented full CRUD operations with rate limiting and automated API documentation."
                }
            ],
            "education": [
                {"degree": "B.S. in Software Engineering", "institution": "University of Washington", "year": "2021"}
            ]
        },
        {
            "format": "pdf",
            "filename": "sophia_rodriguez_data_analyst.pdf",
            "name": "Sophia Rodriguez",
            "title": "Senior Data Analyst & BI Developer",
            "contact": "sophia.rodriguez@email.com | +1 (555) 890-1234 | Chicago, IL | github.com/sophiarodriguez | linkedin.com/in/sophiarodriguez",
            "summary": "Data Analyst with 3.5 years of experience turning complex datasets into actionable business insights. Highly proficient in SQL, Python (Pandas, NumPy), Tableau, Power BI, Excel advanced modeling, and statistical hypothesis testing.",
            "skills": ["SQL", "Python", "Pandas", "NumPy", "Data Analysis", "Tableau", "Power BI", "Excel", "Data Cleaning", "Data Visualization", "ETL", "Statistics", "Git", "Business Intelligence"],
            "experience": [
                {
                    "role": "Senior Data Analyst",
                    "company": "Horizon Financial Group",
                    "period": "2022 - Present",
                    "bullets": [
                        "Formulated complex SQL queries across 50M+ financial transaction rows to identify revenue leakage.",
                        "Automated weekly reporting workflows using Python scripts, saving 15 hours of manual work weekly.",
                        "Designed executive Power BI dashboards with real-time KPI tracking for C-level leadership."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Customer Churn Prediction Dashboard",
                    "tech": "Python, Pandas, Scikit-learn, Tableau",
                    "description": "Built retention forecasting model and interactive dashboard that decreased customer churn by 12%."
                }
            ],
            "education": [
                {"degree": "B.S. in Statistics & Economics", "institution": "University of Illinois at Urbana-Champaign", "year": "2020"}
            ]
        },
        {
            "format": "docx",
            "filename": "david_kim_frontend_react.docx",
            "name": "David Kim",
            "title": "Senior Frontend React Developer",
            "contact": "david.kim@email.com | +1 (555) 321-6549 | Austin, TX | github.com/davidkim | linkedin.com/in/davidkim",
            "summary": "Passionate Frontend Developer with 4 years creating responsive, user-friendly web interfaces using React.js, TypeScript, Next.js, Redux, Tailwind CSS, and Figma. Focused on UI/UX, page speed, and cross-browser accessibility.",
            "skills": ["JavaScript", "TypeScript", "React", "Next.js", "Redux", "HTML5", "CSS3", "Tailwind CSS", "Figma", "UI/UX", "Webpack", "Jest", "Git", "REST APIs"],
            "experience": [
                {
                    "role": "Senior Frontend Developer",
                    "company": "PixelCraft Studios",
                    "period": "2021 - Present",
                    "bullets": [
                        "Built modern SPA interfaces using React and Next.js, improving Web Vitals score from 65 to 98.",
                        "Engineered design system UI component library adopted across 6 cross-functional engineering teams.",
                        "Conducted responsive design audits and accessibility compliance (WCAG 2.1 AA)."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "SaaS Analytics Web Portal",
                    "tech": "React, TypeScript, Tailwind CSS, Chart.js",
                    "description": "Created interactive dashboard interface with responsive grid layouts and client-side charting."
                }
            ],
            "education": [
                {"degree": "B.S. in Computer Science", "institution": "University of Texas at Austin", "year": "2020"}
            ]
        },
        {
            "format": "pdf",
            "filename": "elena_rostova_digital_marketer.pdf",
            "name": "Elena Rostova",
            "title": "Digital Marketing Manager & Growth Strategist",
            "contact": "elena.rostova@email.com | +1 (555) 654-9871 | New York, NY | linkedin.com/in/elenarostova",
            "summary": "Creative and analytical Digital Marketing Specialist with 5+ years driving multi-channel B2B campaigns, SEO, Google Ads, content marketing, and email automation. Proven track record of scaling inbound lead generation.",
            "skills": ["Digital Marketing", "SEO", "Search Engine Optimization", "Google Ads", "SEM", "Content Strategy", "Copywriting", "Email Marketing", "Google Analytics", "Social Media Marketing", "HubSpot", "Brand Management"],
            "experience": [
                {
                    "role": "Marketing Campaign Director",
                    "company": "Vanguard Media Partners",
                    "period": "2020 - Present",
                    "bullets": [
                        "Managed $500K annual PPC search marketing budget across Google Ads and LinkedIn Advertising.",
                        "Scaled organic website search traffic by 180% over 18 months through technical SEO audits.",
                        "Executed targeted email nurture workflows on HubSpot with average open rate of 34%."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Viral Brand Launch Campaign",
                    "tech": "Google Analytics, Meta Ads Manager, HubSpot",
                    "description": "Directed high-converting multi-channel product introduction campaign generating $1.2M pipeline."
                }
            ],
            "education": [
                {"degree": "B.A. in Communications & Marketing", "institution": "New York University", "year": "2019"}
            ]
        },
        {
            "format": "pdf",
            "filename": "rohit_verma_junior_python.pdf",
            "name": "Rohit Verma",
            "title": "Junior Python Developer / Fresher",
            "contact": "rohit.verma@email.com | +1 (555) 111-2233 | San Jose, CA | github.com/rohitverma | linkedin.com/in/rohitverma",
            "summary": "Recent Computer Science graduate with strong fundamentals in Python, Object-Oriented Programming (OOP), Data Structures, Algorithms, and basic web development with Flask. Eager to contribute to software engineering teams.",
            "skills": ["Python", "Flask", "SQL", "Git", "HTML", "CSS", "Data Structures", "Algorithms", "Object-Oriented Programming", "OOP", "Linux", "Problem Solving"],
            "experience": [
                {
                    "role": "Software Engineering Intern",
                    "company": "ByteWave Solutions",
                    "period": "Summer 2023",
                    "bullets": [
                        "Assisted backend team in writing unit tests for Python web services.",
                        "Implemented automated web scraping scripts to extract competitive pricing data.",
                        "Resolved bug tickets and documented internal API endpoints."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Personal Budget Tracker",
                    "tech": "Python, Flask, SQLite, Bootstrap",
                    "description": "Built CRUD web application allowing users to track monthly spending and categorize expenses."
                }
            ],
            "education": [
                {"degree": "B.S. in Computer Science", "institution": "San Jose State University", "year": "2023"}
            ]
        },
        {
            "format": "docx",
            "filename": "chloe_dupont_graphic_designer.docx",
            "name": "Chloe Dupont",
            "title": "Creative Graphic Designer & Brand Stylist",
            "contact": "chloe.dupont@email.com | +1 (555) 999-8888 | Los Angeles, CA | behance.net/chloedupont",
            "summary": "Visual Designer with 4 years experience creating brand identities, print packaging, marketing collateral, vector illustrations, and visual assets using Adobe Creative Suite (Photoshop, Illustrator, InDesign).",
            "skills": ["Graphic Design", "Adobe Photoshop", "Adobe Illustrator", "InDesign", "Typography", "Brand Identity", "Logo Design", "Print Production", "Visual Design", "Creative Direction", "Figma"],
            "experience": [
                {
                    "role": "Senior Visual Graphic Designer",
                    "company": "Lumina Creative Studio",
                    "period": "2021 - Present",
                    "bullets": [
                        "Designed cohesive corporate branding packages for 25+ retail and consumer product clients.",
                        "Produced custom vector typography and packaging mockups for national retail distribution.",
                        "Coordinated pre-press color proofing and print packaging specifications."
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Artisanal Coffee Packaging Rebrand",
                    "tech": "Illustrator, Photoshop, InDesign",
                    "description": "Created bespoke packaging label series nominated for American Graphic Design Award."
                }
            ],
            "education": [
                {"degree": "B.F.A. in Graphic Design", "institution": "Rhode Island School of Design", "year": "2020"}
            ]
        }
    ]

    for cand in candidates:
        out_path = os.path.join(target_dir, cand['filename'])
        if cand['format'] == 'pdf':
            create_pdf_resume(
                out_path, cand['name'], cand['title'], cand['contact'],
                cand['summary'], cand['skills'], cand['experience'],
                cand['education'], cand['projects']
            )
            print(f"Generated PDF: {cand['filename']}")
        else:
            create_docx_resume(
                out_path, cand['name'], cand['title'], cand['contact'],
                cand['summary'], cand['skills'], cand['experience'],
                cand['education'], cand['projects']
            )
            print(f"Generated DOCX: {cand['filename']}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resumes_dir = os.path.join(current_dir, "resumes")
    generate_all_resumes(resumes_dir)
