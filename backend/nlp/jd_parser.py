"""
Job Description (JD) Parser.
Extracts Job Title, required experience, education level, and splits skills
into Must-Have (Required) vs Good-to-Have (Preferred) based on contextual clues.
"""

import re
from typing import Any, Dict, List, Set

from backend.nlp.entity_extractor import EntityExtractor
from backend.nlp.skills_db import ALL_SKILLS, get_canonical_skill, get_category_for_skill


class JobDescriptionParser:
    """Parses Job Descriptions into structured criteria for matching."""

    @classmethod
    def parse_job_title(cls, text: str) -> str:
        """Infer or extract the job title from top lines."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Look for common title indicators
            title_match = re.search(
                r"(?:job\s+title|role|position|opening)\s*:\s*(.+)",
                line,
                re.IGNORECASE
            )
            if title_match:
                return title_match.group(1).strip()
            # If line is short and contains common job keywords
            if len(line.split()) <= 6 and re.search(
                r"\b(engineer|developer|scientist|analyst|architect|manager|lead|intern|designer)\b",
                line,
                re.IGNORECASE
            ):
                return line.strip()

        return "Target Position"

    @classmethod
    def extract_experience_required(cls, text: str) -> float:
        """Extract required minimum years of experience from JD."""
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant\s+)?experience",
            r"(?:minimum|at\s+least)\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\s*-\s*\d+\s*(?:years?|yrs?)(?:\s+of)?\s+experience"
        ]

        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # Check for senior / lead in title
        if re.search(r"\b(senior|sr\.|lead|principal)\b", text, re.IGNORECASE):
            return 5.0
        elif re.search(r"\b(intern|fresher|junior|jr\.|entry)\b", text, re.IGNORECASE):
            return 0.0

        return 2.0  # Default baseline if not mentioned

    @classmethod
    def extract_education_required(cls, text: str) -> Dict[str, Any]:
        """Extract required education level from JD."""
        target_lower = text.lower()
        required_degree = "Bachelor's Degree"
        degree_rank = 2

        if re.search(r"\b(phd|doctorate)\b", target_lower):
            required_degree = "Doctorate / Ph.D."
            degree_rank = 4
        elif re.search(r"\b(master|m\.tech|ms|msc|mba)\b", target_lower):
            required_degree = "Master's Degree"
            degree_rank = 3
        elif re.search(r"\b(bachelor|b\.tech|btech|be|bs|bsc|bca)\b", target_lower):
            required_degree = "Bachelor's Degree"
            degree_rank = 2
        elif re.search(r"\b(diploma|associate)\b", target_lower):
            required_degree = "Diploma / Associate"
            degree_rank = 1

        return {
            "required_degree": required_degree,
            "degree_rank": degree_rank
        }

    @classmethod
    def extract_skills_with_priority(cls, text: str) -> Dict[str, List[str]]:
        """
        Classifies skills in the JD into 'must_have' and 'good_to_have'
        by identifying sections like 'Requirements / Must Haves' vs 'Preferred / Plus / Bonus'.
        """
        # Split text into sections if possible
        sections = re.split(r"\n(?=[A-Z0-9\s\-_]{3,}:|\b(?:Requirements|Qualifications|Must Have|Preferred|Good to have|Nice to have)\b)", text, flags=re.IGNORECASE)

        must_have_skills: Set[str] = set()
        good_to_have_skills: Set[str] = set()
        all_detected: Set[str] = set()

        # Helper to extract skills from a chunk
        def extract_from_chunk(chunk: str) -> Set[str]:
            res = set()
            chunk_lower = chunk.lower()
            for s in sorted(ALL_SKILLS, key=len, reverse=True):
                escaped = re.escape(s)
                pattern = rf"(?:^|[\s,;:\/\(\)\[\]•\-\|\n]){escaped}(?:[\s,;:\/\(\)\[\]•\-\|\n]|$)"
                if re.search(pattern, chunk_lower):
                    res.add(get_canonical_skill(s))
            return res

        for chunk in sections:
            header = chunk.split("\n")[0].lower()
            skills_in_chunk = extract_from_chunk(chunk)
            all_detected.update(skills_in_chunk)

            if re.search(r"\b(preferred|nice\s+to\s+have|good\s+to\s+have|bonus|plus|desirable)\b", header):
                good_to_have_skills.update(skills_in_chunk)
            elif re.search(r"\b(must\s+have|required|requirements|qualifications|essential|mandatory)\b", header):
                must_have_skills.update(skills_in_chunk)

        # Fallback if no specific section headers were detected
        if not must_have_skills and not good_to_have_skills:
            # All detected skills become must-have, top 70% must-have
            all_list = list(all_detected)
            must_have_skills = set(all_list)

        # Remove must_have duplicates from good_to_have
        good_to_have_skills = good_to_have_skills - must_have_skills

        return {
            "must_have": sorted([s.title() for s in must_have_skills]),
            "good_to_have": sorted([s.title() for s in good_to_have_skills]),
            "all_jd_skills": sorted([s.title() for s in all_detected])
        }

    @classmethod
    def parse(cls, jd_text: str) -> Dict[str, Any]:
        """Full parse of the Job Description."""
        clean_text = EntityExtractor.extract_contact_info(jd_text)  # not needed, use docparser
        title = cls.parse_job_title(jd_text)
        exp_required = cls.extract_experience_required(jd_text)
        edu_required = cls.extract_education_required(jd_text)
        skills = cls.extract_skills_with_priority(jd_text)

        return {
            "title": title,
            "min_experience_years": exp_required,
            "education": edu_required,
            "skills": skills,
            "raw_text": jd_text
        }
