"""
Document parser module supporting PDF, DOCX, and TXT files.
Extracts clean, normalized text and segments resumes into logical sections.
"""

import io
import os
import re
import zipfile
from typing import Dict, Optional
import xml.etree.ElementTree as ET


class DocumentParser:
    """Extracts text and structure from resumes in various document formats."""

    @staticmethod
    def extract_text_from_txt(content: bytes) -> str:
        """Decode TXT with utf-8, fallback to latin-1."""
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                return content.decode(enc)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="ignore")

    @staticmethod
    def extract_text_from_pdf(content: bytes) -> str:
        """Extract text from PDF using pypdf, with fallback."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n".join(pages)
        except Exception:
            # Fallback stream string extraction for simple PDFs
            raw_str = content.decode("latin-1", errors="ignore")
            matches = re.findall(r"\((.*?)\)[\s]*T[jJ]", raw_str)
            if matches:
                return " ".join(matches)
            return ""

    @staticmethod
    def extract_text_from_docx(content: bytes) -> str:
        """Extract text from DOCX using python-docx with pure-python zip/XML fallback."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            return "\n".join(paragraphs)
        except Exception:
            # Pure-python fallback extracting word/document.xml
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as docx_zip:
                    xml_content = docx_zip.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    texts = [node.text for node in tree.iter() if node.text and node.text.strip()]
                    return "\n".join(texts)
            except Exception:
                return ""

    @classmethod
    def parse(cls, filename: str, content: bytes) -> str:
        """Parse document content based on filename extension."""
        ext = os.path.splitext(filename)[1].lower()
        raw_text = ""
        if ext in [".pdf"]:
            raw_text = cls.extract_text_from_pdf(content)
        elif ext in [".docx"]:
            raw_text = cls.extract_text_from_docx(content)
        elif ext in [".txt", ".md", ".rtf"]:
            raw_text = cls.extract_text_from_txt(content)
        else:
            # Attempt plain text decoding
            raw_text = cls.extract_text_from_txt(content)

        return cls.clean_text(raw_text)

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted resume text."""
        if not text:
            return ""
        # Normalize newlines
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove consecutive non-breaking spaces & tabs
        text = re.sub(r"[ \t]+", " ", text)
        # Remove non-printable characters keeping common punctuation
        text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
        # Collapse multiple newlines down to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def segment_sections(text: str) -> Dict[str, str]:
        """
        Segment resume into standard sections:
        Contact, Summary, Experience, Education, Skills, Projects, Certifications.
        """
        section_patterns = {
            "skills": r"(?:technical\s+skills|core\s+competencies|technologies|skills\s+&*|skills\s+and\s+tools|skills)",
            "experience": r"(?:work\s+experience|professional\s+experience|employment\s+history|experience|work\s+history)",
            "education": r"(?:education|academic\s+background|educational\s+qualifications|academics)",
            "projects": r"(?:projects|key\s+projects|academic\s+projects|personal\s+projects)",
            "certifications": r"(?:certifications|licenses\s+and\s+certifications|certificates|courses)",
            "summary": r"(?:professional\s+summary|summary|profile|about\s+me|career\s+objective|objective)"
        }

        # Build combined regex for section headers
        headers_regex = r"(?:^|\n)(?P<header>" + "|".join(
            f"(?P<{k}>{pat})" for k, pat in section_patterns.items()
        ) + r")(?:\s*[:\-\n])"

        matches = list(re.finditer(headers_regex, text, re.IGNORECASE))
        sections: Dict[str, str] = {
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "certifications": "",
            "raw": text
        }

        if not matches:
            # If no clear section headers, place text in general bucket
            sections["summary"] = text[:500]
            sections["experience"] = text
            return sections

        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sec_text = text[start:end].strip()

            for key in section_patterns:
                if match.group(key):
                    sections[key] = sec_text
                    break

        return sections
