"""
Resume Text & Metadata Extractor Module.
Supports PDF (.pdf), Word Document (.docx), and Plain Text (.txt) formats.
"""

import os
import re
from typing import Dict, Any, Optional
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts raw text from a PDF file using pypdf."""
    text_content = []
    try:
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        print(f"[Error] Failed to read PDF '{file_path}': {e}")
    return "\n".join(text_content)


def extract_text_from_docx(file_path: str) -> str:
    """Extracts raw text from a DOCX file using python-docx."""
    text_content = []
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_content.append(" | ".join(row_text))
    except Exception as e:
        print(f"[Error] Failed to read DOCX '{file_path}': {e}")
    return "\n".join(text_content)


def extract_text_from_txt(file_path: str) -> str:
    """Extracts raw text from a standard TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[Error] Failed to read TXT '{file_path}': {e}")
        return ""


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts contact information such as email, phone number, and LinkedIn/GitHub links.
    """
    # Email Regex
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None

    # Phone Regex (covers international, US formats, etc.)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    phone = None
    if phones:
        # Search for full matched string
        matches = re.finditer(phone_pattern, text)
        for m in matches:
            candidate_phone = m.group(0).strip()
            if len(re.sub(r'\D', '', candidate_phone)) >= 10:
                phone = candidate_phone
                break

    # LinkedIn / GitHub URLs
    linkedin = re.findall(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    github = re.findall(r'(github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None
    }


def extract_candidate_name(text: str, filename: str) -> str:
    """
    Infers candidate name from resume header or derives it from filename.
    """
    # Look at the first 3 lines of text
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:3]:
        # Typical name: 2-3 words, no numbers, no special symbols, length < 35
        if re.match(r'^[A-Z][a-zA-Z]+(\s[A-Z][a-zA-Z]+){1,2}$', line) and len(line) < 35:
            return line

    # Fallback to formatting filename: 'alex_turner_senior_python_dev.pdf' -> 'Alex Turner'
    base = os.path.splitext(os.path.basename(filename))[0]
    clean_base = re.sub(r'(_|-)', ' ', base)
    words = clean_base.split()
    if len(words) >= 2:
        return f"{words[0].capitalize()} {words[1].capitalize()}"
    return words[0].capitalize() if words else "Unknown Candidate"


def extract_resume_data(file_path: str) -> Dict[str, Any]:
    """
    Unified extractor entrypoint. Parses file, gathers text, metadata and contacts.
    """
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        raw_text = extract_text_from_txt(file_path)
    else:
        raw_text = ""

    contacts = extract_contact_info(raw_text)
    name = extract_candidate_name(raw_text, filename)

    return {
        "filename": filename,
        "file_path": file_path,
        "file_type": ext.replace(".", "").upper(),
        "candidate_name": name,
        "email": contacts["email"],
        "phone": contacts["phone"],
        "linkedin": contacts["linkedin"],
        "github": contacts["github"],
        "raw_text": raw_text,
        "char_count": len(raw_text),
        "word_count": len(raw_text.split())
    }
