"""
Matching and Ranking Engine with Explainable AI (XAI).
Calculates multi-dimensional match scores (semantic, skills, experience, education),
ranks candidates, and generates transparent recruiter decision rationales.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


class MatcherEngine:
    """Calculates candidate-job description relevance and generates explainable reports."""

    def __init__(self):
        # We check if scikit-learn is available, otherwise use pure Python TF-IDF cosine similarity
        self.has_sklearn = False
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            self.has_sklearn = True
        except ImportError:
            self.has_sklearn = False

    def compute_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute semantic similarity score between candidate text and JD.
        Uses Scikit-Learn TfidfVectorizer if available, otherwise pure-Python TF-IDF.
        """
        if not text_a.strip() or not text_b.strip():
            return 0.0

        if self.has_sklearn:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity

                vectorizer = TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=5000
                )
                tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
                sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(min(1.0, max(0.0, sim)))
            except Exception:
                pass

        # Pure-Python Token / N-Gram Vectorizer fallback (Zero-dependency guarantee)
        return self._pure_python_cosine_similarity(text_a, text_b)

    def _pure_python_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """Pure-Python word frequency cosine similarity fallback."""
        def tokenize(text: str) -> List[str]:
            words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
            # Basic common stopwords
            stopwords = {
                "the", "and", "in", "of", "to", "a", "with", "for", "on", "as", "is",
                "at", "by", "an", "be", "this", "which", "or", "from", "that", "are",
                "your", "will", "our", "you", "we", "all", "have", "can", "has"
            }
            return [w for w in words if w not in stopwords]

        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0

        # Term counts
        freq_a: Dict[str, int] = {}
        for t in tokens_a:
            freq_a[t] = freq_a.get(t, 0) + 1

        freq_b: Dict[str, int] = {}
        for t in tokens_b:
            freq_b[t] = freq_b.get(t, 0) + 1

        all_terms = set(freq_a.keys()).union(set(freq_b.keys()))

        dot_product = sum(freq_a.get(t, 0) * freq_b.get(t, 0) for t in all_terms)
        norm_a = math.sqrt(sum(v ** 2 for v in freq_a.values()))
        norm_b = math.sqrt(sum(v ** 2 for v in freq_b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        raw_sim = dot_product / (norm_a * norm_b)
        # Scale to 0-1 range
        return float(min(1.0, max(0.0, raw_sim)))

    @staticmethod
    def compute_skill_scores(
        candidate_skills: List[str],
        must_have: List[str],
        good_to_have: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate candidate skills against Must-Have and Good-to-Have JD skills.
        Returns matched, missing, and weighted skill coverage score.
        """
        cand_set = {s.lower().strip() for s in candidate_skills}
        must_set = {s.lower().strip() for s in must_have}
        good_set = {s.lower().strip() for s in good_to_have}

        matched_must = [s for s in must_have if s.lower().strip() in cand_set]
        missing_must = [s for s in must_have if s.lower().strip() not in cand_set]

        matched_good = [s for s in good_to_have if s.lower().strip() in cand_set]
        missing_good = [s for s in good_to_have if s.lower().strip() not in cand_set]

        # Calculate coverage percentages
        must_ratio = len(matched_must) / max(1, len(must_have)) if must_have else 1.0
        good_ratio = len(matched_good) / max(1, len(good_to_have)) if good_to_have else 1.0

        if must_have and good_to_have:
            weighted_skill_score = (0.75 * must_ratio) + (0.25 * good_ratio)
        elif must_have:
            weighted_skill_score = must_ratio
        elif good_to_have:
            weighted_skill_score = good_ratio
        else:
            # If no skills mentioned in JD, give default neutral score
            weighted_skill_score = 0.5

        return {
            "score": round(weighted_skill_score * 100, 1),
            "matched_must": matched_must,
            "missing_must": missing_must,
            "matched_good": matched_good,
            "missing_good": missing_good,
            "must_have_coverage_pct": round(must_ratio * 100, 1),
            "good_to_have_coverage_pct": round(good_ratio * 100, 1)
        }

    @staticmethod
    def compute_experience_score(candidate_years: float, required_years: float) -> Dict[str, Any]:
        """
        Calculates experience score based on candidate vs required years.
        Gives 100% if candidate matches or exceeds required years.
        Partial credit given for near matches.
        """
        if required_years <= 0:
            score = 100.0
            verdict = "Requirement met (No prior experience mandated)"
        elif candidate_years >= required_years:
            score = 100.0
            delta = round(candidate_years - required_years, 1)
            if delta > 0:
                verdict = f"Exceeds required by {delta} yr{'s' if delta != 1 else ''}"
            else:
                verdict = "Exactly matches required experience"
        else:
            ratio = candidate_years / required_years
            score = round(ratio * 100, 1)
            gap = round(required_years - candidate_years, 1)
            verdict = f"Short by {gap} yr{'s' if gap != 1 else ''}"

        return {
            "score": score,
            "candidate_years": candidate_years,
            "required_years": required_years,
            "verdict": verdict
        }

    @staticmethod
    def compute_education_score(candidate_rank: int, required_rank: int, cand_degree: str, req_degree: str) -> Dict[str, Any]:
        """
        Calculates education alignment score based on degree ranks.
        Rank 4: PhD, 3: Master's, 2: Bachelor's, 1: Diploma, 0: None.
        """
        if required_rank <= 0 or candidate_rank >= required_rank:
            score = 100.0
            verdict = f"Qualified ({cand_degree} meets requirement)"
        elif candidate_rank == required_rank - 1:
            score = 75.0
            verdict = f"Near match ({cand_degree} vs required {req_degree})"
        else:
            score = 50.0
            verdict = f"Below preferred requirement ({cand_degree} vs {req_degree})"

        return {
            "score": score,
            "candidate_degree": cand_degree,
            "required_degree": req_degree,
            "verdict": verdict
        }

    def evaluate_candidate(
        self,
        candidate_data: Dict[str, Any],
        raw_resume_text: str,
        jd_data: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single candidate against a Job Description.
        Returns final weighted score (0 - 100), breakdown sub-scores, and XAI rationales.
        """
        # Default weights
        w = {
            "semantic": 0.35,
            "skills": 0.40,
            "experience": 0.15,
            "education": 0.10
        }
        if weights:
            w.update(weights)

        # 1. Semantic Similarity
        sem_sim = self.compute_semantic_similarity(raw_resume_text, jd_data.get("raw_text", ""))
        sem_score = round(sem_sim * 100, 1)

        # 2. Skills Matching
        cand_skills = candidate_data.get("skills", {}).get("all_skills", [])
        jd_skills = jd_data.get("skills", {})
        must_have = jd_skills.get("must_have", [])
        good_to_have = jd_skills.get("good_to_have", [])
        skills_eval = self.compute_skill_scores(cand_skills, must_have, good_to_have)

        # 3. Experience Matching
        cand_exp = candidate_data.get("experience", {}).get("years", 0.0)
        req_exp = jd_data.get("min_experience_years", 0.0)
        exp_eval = self.compute_experience_score(cand_exp, req_exp)

        # 4. Education Matching
        cand_edu_rank = candidate_data.get("education", {}).get("degree_rank", 2)
        cand_deg_name = candidate_data.get("education", {}).get("highest_degree", "Bachelor's Degree")
        req_edu_rank = jd_data.get("education", {}).get("degree_rank", 2)
        req_deg_name = jd_data.get("education", {}).get("required_degree", "Bachelor's Degree")
        edu_eval = self.compute_education_score(cand_edu_rank, req_edu_rank, cand_deg_name, req_deg_name)

        # Composite Final Score
        final_score = (
            w["semantic"] * sem_score +
            w["skills"] * skills_eval["score"] +
            w["experience"] * exp_eval["score"] +
            w["education"] * edu_eval["score"]
        )
        final_score = round(final_score, 1)

        # Determine Recommendation & Tier
        if final_score >= 80.0:
            tier = "Strong Fit"
            tier_badge = "success"
            action = "Fast-track to Recruiter Phone Screen"
        elif final_score >= 65.0:
            tier = "Moderate Fit"
            tier_badge = "warning"
            action = "Review Skill Gaps for Technical Interview"
        elif final_score >= 50.0:
            tier = "Potential Fit"
            tier_badge = "info"
            action = "Hold for Secondary Screening"
        else:
            tier = "Low Match"
            tier_badge = "danger"
            action = "Does not meet core qualifications"

        # Explainable AI Insights
        strengths = []
        if skills_eval["matched_must"]:
            strengths.append(f"Demonstrates mastery in {len(skills_eval['matched_must'])} key required skills ({', '.join(skills_eval['matched_must'][:4])})")
        if exp_eval["score"] == 100.0:
            strengths.append(f"Experience criteria satisfied: {exp_eval['verdict']}")
        if sem_score >= 60.0:
            strengths.append(f"High contextual relevance with overall job specifications ({sem_score}% match)")

        gap_areas = []
        if skills_eval["missing_must"]:
            gap_areas.append(f"Missing mandatory requirements: {', '.join(skills_eval['missing_must'][:5])}")
        if exp_eval["score"] < 100.0:
            gap_areas.append(f"Experience gap: {exp_eval['verdict']}")
        if not gap_areas:
            gap_areas.append("No critical qualification gaps detected")

        return {
            "candidate_name": candidate_data.get("candidate_name", "Candidate"),
            "filename": candidate_data.get("filename", "resume.pdf"),
            "contact": candidate_data.get("contact", {}),
            "final_score": final_score,
            "tier": tier,
            "tier_badge": tier_badge,
            "recommended_action": action,
            "sub_scores": {
                "semantic": {
                    "score": sem_score,
                    "weight_pct": int(w["semantic"] * 100)
                },
                "skills": {
                    "score": skills_eval["score"],
                    "weight_pct": int(w["skills"] * 100),
                    "matched_must": skills_eval["matched_must"],
                    "missing_must": skills_eval["missing_must"],
                    "matched_good": skills_eval["matched_good"],
                    "missing_good": skills_eval["missing_good"]
                },
                "experience": {
                    "score": exp_eval["score"],
                    "weight_pct": int(w["experience"] * 100),
                    "years": cand_exp,
                    "verdict": exp_eval["verdict"]
                },
                "education": {
                    "score": edu_eval["score"],
                    "weight_pct": int(w["education"] * 100),
                    "degree": cand_deg_name,
                    "verdict": edu_eval["verdict"]
                }
            },
            "candidate_skills_by_category": candidate_data.get("skills", {}).get("by_category", {}),
            "total_candidate_skills": candidate_data.get("skills", {}).get("total_count", 0),
            "strengths": strengths,
            "gap_areas": gap_areas
        }

    def rank_candidates(
        self,
        evaluated_candidates: List[Dict[str, Any]],
        min_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Rank evaluated candidates in descending order of final score."""
        filtered = [c for c in evaluated_candidates if c["final_score"] >= min_threshold]
        ranked = sorted(filtered, key=lambda x: x["final_score"], reverse=True)
        for i, cand in enumerate(ranked):
            cand["rank"] = i + 1
        return ranked
