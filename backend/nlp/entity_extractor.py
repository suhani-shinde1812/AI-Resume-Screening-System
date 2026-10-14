"""
Entity Extractor module for resumes.
Extracts Candidate Name, Contact Info (Email, Phone, Links), Skills,
Years of Experience, Education degrees, and Certifications.
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.nlp.skills_db import (
    ALL_SKILLS,
    get_canonical_skill,
    get_category_for_skill,
    SKILL_CATEGORIES
)


class EntityExtractor:
    """Extracts structured entities from resume raw text and sections."""

    # Regex patterns for contact information
    EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    PHONE_REGEX = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{10}\b"
    URL_REGEX = r"(?:https?:\/\/)?(?:www\.)?(linkedin\.com\/in\/[A-Za-z0-9_-]+|github\.com\/[A-Za-z0-9_-]+)"

    # Education degree hierarchies
    DEGREE_HIERARCHY = {
        "phd": ("Doctorate / Ph.D.", 4),
        "doctorate": ("Doctorate / Ph.D.", 4),
        "master": ("Master's Degree", 3),
        "m.tech": ("Master's Degree", 3),
        "mtech": ("Master's Degree", 3),
        "ms": ("Master's Degree", 3),
        "m.s": ("Master's Degree", 3),
        "msc": ("Master's Degree", 3),
        "m.sc": ("Master's Degree", 3),
        "mba": ("Master's Degree", 3),
        "bachelor": ("Bachelor's Degree", 2),
        "b.tech": ("Bachelor's Degree", 2),
        "btech": ("Bachelor's Degree", 2),
        "be": ("Bachelor's Degree", 2),
        "b.e": ("Bachelor's Degree", 2),
        "bs": ("Bachelor's Degree", 2),
        "b.s": ("Bachelor's Degree", 2),
        "bsc": ("Bachelor's Degree", 2),
        "b.sc": ("Bachelor's Degree", 2),
        "bca": ("Bachelor's Degree", 2),
        "diploma": ("Diploma / Associate", 1),
        "associate": ("Diploma / Associate", 1)
    }

    @classmethod
    def extract_contact_info(cls, text: str) -> Dict[str, Any]:
        """Extract email, phone, and professional profile links."""
        emails = re.findall(cls.EMAIL_REGEX, text, re.IGNORECASE)
        phones = re.findall(cls.PHONE_REGEX, text)
        urls = re.findall(cls.URL_REGEX, text, re.IGNORECASE)

        cleaned_phones = []
        for p in phones:
            digits = re.sub(r"\D", "", p)
            if 7 <= len(digits) <= 15:
                cleaned_phones.append(p.strip())

        linkedin = next((u for u in urls if "linkedin" in u.lower()), None)
        github = next((u for u in urls if "github" in u.lower()), None)

        return {
            "email": emails[0] if emails else None,
            "phone": cleaned_phones[0] if cleaned_phones else None,
            "linkedin": f"https://{linkedin}" if linkedin and not linkedin.startswith("http") else linkedin,
            "github": f"https://{github}" if github and not github.startswith("http") else github
        }

    @classmethod
    def extract_name(cls, text: str, email: Optional[str] = None) -> str:
        """
        Extract the candidate's name typically located in the first few lines of the resume.
        Filters out common header words like Resume, Curriculum Vitae, Contact, etc.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:6]:
            # Filter out email, phone, addresses, URLs, and section titles
            if re.search(cls.EMAIL_REGEX, line) or re.search(cls.PHONE_REGEX, line):
                continue
            if re.search(r"\b(resume|curriculum|vitae|page|profile|summary|contact|email|phone|objective)\b", line, re.IGNORECASE):
                continue
            # Words check: Names are typically 2 to 4 capitalized words without special chars
            words = line.split()
            if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.\'-]+$", w) for w in words):
                # Ensure it's not all numbers or weird symbols
                return line.strip()

        # Fallback from email handle if available
        if email:
            handle = email.split("@")[0]
            clean_handle = re.sub(r"[0-9_\.]+", " ", handle).title().strip()
            if clean_handle:
                return clean_handle

        return "Candidate"

    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, Any]:
        """
        Extract skills based on boundary-aware matching against our curated taxonomy.
        Groups extracted skills by domain category and provides canonical names.
        """
        text_lower = text.lower()
        extracted_canonical: Set[str] = set()
        by_category: Dict[str, List[str]] = {}

        # Sort skills by length descending to match multi-word phrases first
        # e.g., "natural language processing" before "nlp"
        sorted_skills = sorted(ALL_SKILLS, key=len, reverse=True)

        for skill in sorted_skills:
            # Word boundary matching
            # Note: special characters in skills like c++, c#, .net need regex escaping
            escaped = re.escape(skill)
            # Require word boundary or punctuation boundary
            pattern = rf"(?:^|[\s,;:\/\(\)\[\]•\-\|\n]){escaped}(?:[\s,;:\/\(\)\[\]•\-\|\n]|$)"
            if re.search(pattern, text_lower):
                canonical = get_canonical_skill(skill)
                if canonical not in extracted_canonical:
                    extracted_canonical.add(canonical)
                    category = get_category_for_skill(canonical)
                    by_category.setdefault(category, []).append(canonical.title())

        # Flatten list for overall skills
        all_matched = sorted([s.title() for s in extracted_canonical])

        return {
            "all_skills": all_matched,
            "total_count": len(all_matched),
            "by_category": by_category
        }

    @classmethod
    def extract_experience(cls, text: str, sections: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extract years of experience using:
        1. Explicit statements like 'X+ years of experience'
        2. Date range calculations in experience section (e.g. 2019 - 2023, Jan 2021 - Present)
        """
        current_year = datetime.now().year
        total_years = 0.0
        explicit_matches = []

        # Check explicit statements first
        exp_statements = re.findall(
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)",
            text,
            re.IGNORECASE
        )
        if exp_statements:
            explicit_matches = [float(x) for x in exp_statements if float(x) <= 40]
            if explicit_matches:
                total_years = max(explicit_matches)

        # Date range parsing
        target_text = ""
        if sections and sections.get("experience"):
            target_text = sections["experience"]
        else:
            target_text = text

        # Regex for year ranges like 2018 - 2022, 2020 - Present, 2019 to Current
        range_pattern = r"\b(19\d\d|20\d\d)\s*(?:-|–|—|to)\s*(19\d\d|20\d\d|present|current|now)\b"
        ranges = re.findall(range_pattern, target_text, re.IGNORECASE)

        calculated_years = 0.0
        for start_str, end_str in ranges:
            start_yr = int(start_str)
            if end_str.lower() in ["present", "current", "now"]:
                end_yr = current_year
            else:
                end_yr = int(end_str)

            if 1970 <= start_yr <= current_year and start_yr <= end_yr <= current_year + 1:
                duration = max(0.5, end_yr - start_yr)
                calculated_years += duration

        # Combine logic: if explicit was found, take max of explicit and calculated
        final_years = max(total_years, min(calculated_years, 35.0))
        # Round to 1 decimal place
        final_years = round(final_years, 1)

        seniority_level = "Entry Level (< 2 yrs)"
        if final_years >= 8:
            seniority_level = "Lead / Staff (8+ yrs)"
        elif final_years >= 5:
            seniority_level = "Senior (5 - 8 yrs)"
        elif final_years >= 2:
            seniority_level = "Mid Level (2 - 5 yrs)"

        return {
            "years": final_years,
            "seniority_level": seniority_level,
            "explicit_stated": explicit_matches[0] if explicit_matches else None
        }

    @classmethod
    def extract_education(cls, text: str, sections: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extract degrees and educational level.
        Detects highest level achieved based on standard hierarchy.
        """
        target_text = ""
        if sections and sections.get("education"):
            target_text = sections["education"]
        else:
            target_text = text

        target_lower = target_text.lower()
        found_degrees = []
        highest_rank = 0
        highest_degree = "High School / Unspecified"

        for key, (deg_name, rank) in cls.DEGREE_HIERARCHY.items():
            pattern = rf"\b{re.escape(key)}\b"
            if re.search(pattern, target_lower):
                if deg_name not in found_degrees:
                    found_degrees.append(deg_name)
                if rank > highest_rank:
                    highest_rank = rank
                    highest_degree = deg_name

        # Detect field/major
        majors = []
        field_patterns = [
            r"computer\s+science", r"information\s+technology", r"data\s+science",
            r"artificial\s+intelligence", r"machine\s+learning", r"software\s+engineering",
            r"electrical\s+engineering", r"electronics", r"mechanical\s+engineering",
            r"business\s+administration", r"statistics", r"mathematics"
        ]
        for field in field_patterns:
            if re.search(rf"\b{field}\b", target_lower):
                clean_field = field.replace(r"\s+", " ").title()
                if clean_field not in majors:
                    majors.append(clean_field)

        return {
            "highest_degree": highest_degree,
            "degree_rank": highest_rank,
            "all_degrees": found_degrees,
            "majors": majors
        }

    @classmethod
    def extract_all(cls, raw_text: str, filename: str = "resume.pdf") -> Dict[str, Any]:
        """Full extraction pipeline for a resume."""
        from backend.parsers.doc_parser import DocumentParser

        sections = DocumentParser.segment_sections(raw_text)
        contact = cls.extract_contact_info(raw_text)
        name = cls.extract_name(raw_text, contact.get("email"))
        skills = cls.extract_skills(raw_text)
        experience = cls.extract_experience(raw_text, sections)
        education = cls.extract_education(raw_text, sections)

        return {
            "filename": filename,
            "candidate_name": name,
            "contact": contact,
            "skills": skills,
            "experience": experience,
            "education": education,
            "sections": {k: v[:200] + ("..." if len(v) > 200 else "") for k, v in sections.items() if k != "raw"}
        }
