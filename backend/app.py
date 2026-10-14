"""
FastAPI Backend Application for AI Resume Screening System.
Provides RESTful APIs for parsing Job Descriptions, evaluating resumes,
ranking candidates, and serving the interactive Recruiter Dashboard.
"""

import io
import json
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.nlp.entity_extractor import EntityExtractor
from backend.nlp.jd_parser import JobDescriptionParser
from backend.nlp.matcher import MatcherEngine
from backend.parsers.doc_parser import DocumentParser
from backend.utils.sample_data import SAMPLE_JDS, SAMPLE_RESUMES

app = FastAPI(
    title="AI Resume Screening & Ranking API",
    description="Intelligent ATS decision-support system evaluating candidate resumes against job descriptions.",
    version="1.0.0"
)

# Enable CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

matcher = MatcherEngine()

# Ensure frontend path exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# Pydantic Schemas
class ScreeningRequest(BaseModel):
    jd_text: str
    resumes: Optional[List[Dict[str, str]]] = None  # [{'filename': ..., 'text': ...}]
    weights: Optional[Dict[str, float]] = None
    anonymize: bool = False
    min_threshold: float = 0.0


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the Recruiter Web Application UI."""
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AI Resume Screening System API</h1><p>Frontend loading...</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint displaying engine capabilities."""
    return {
        "status": "online",
        "engine": "AI Resume Screener v1.0",
        "sklearn_loaded": matcher.has_sklearn,
        "supported_formats": [".pdf", ".docx", ".txt", ".md"]
    }


@app.get("/api/samples")
async def get_samples():
    """Retrieve preloaded realistic sample Job Descriptions and resumes."""
    return {
        "jds": SAMPLE_JDS,
        "resumes": SAMPLE_RESUMES
    }


@app.post("/api/parse-jd")
async def parse_job_description(payload: Dict[str, str]):
    """Parse a raw Job Description and return structured criteria."""
    jd_text = payload.get("jd_text", "").strip()
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    parsed_jd = JobDescriptionParser.parse(jd_text)
    return {
        "success": True,
        "criteria": parsed_jd
    }


@app.post("/api/screen")
async def screen_candidates(
    jd_text: str = Form(...),
    weights_json: Optional[str] = Form(None),
    anonymize: bool = Form(False),
    min_threshold: float = Form(0.0),
    resume_files: List[UploadFile] = File(None)
):
    """
    Main screening pipeline: Ingests JD text and multiple resume files (PDF, DOCX, TXT),
    parses entities, computes scores, and outputs ranked candidates with XAI insights.
    """
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required.")

    weights = None
    if weights_json:
        try:
            weights = json.loads(weights_json)
        except Exception:
            weights = None

    # Parse Job Description
    parsed_jd = JobDescriptionParser.parse(jd_text)

    # Ingest resumes
    processed_resumes = []
    if resume_files:
        for file in resume_files:
            try:
                content = await file.read()
                raw_text = DocumentParser.parse(file.filename, content)
                if raw_text.strip():
                    extracted = EntityExtractor.extract_all(raw_text, filename=file.filename)
                    processed_resumes.append({
                        "raw_text": raw_text,
                        "data": extracted
                    })
            except Exception as e:
                # Still record failed file with notice
                continue

    if not processed_resumes:
        raise HTTPException(status_code=400, detail="No readable resumes provided. Please upload valid PDF, DOCX, or TXT files.")

    # Evaluate each candidate
    evaluated_list = []
    for item in processed_resumes:
        cand_data = item["data"]
        raw_text = item["raw_text"]

        evaluation = matcher.evaluate_candidate(
            candidate_data=cand_data,
            raw_resume_text=raw_text,
            jd_data=parsed_jd,
            weights=weights
        )

        # Apply bias-free anonymization if selected
        if anonymize:
            evaluation["candidate_name"] = f"Candidate #{len(evaluated_list) + 1}"
            evaluation["contact"] = {
                "email": "[Protected for Blind Screening]",
                "phone": "[Protected for Blind Screening]",
                "linkedin": None,
                "github": None
            }

        evaluated_list.append(evaluation)

    # Rank candidates
    ranked_candidates = matcher.rank_candidates(evaluated_list, min_threshold=min_threshold)

    # Compute pool analytics
    scores = [c["final_score"] for c in ranked_candidates]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    tier_distribution = {
        "Strong Fit": sum(1 for c in ranked_candidates if c["tier"] == "Strong Fit"),
        "Moderate Fit": sum(1 for c in ranked_candidates if c["tier"] == "Moderate Fit"),
        "Potential Fit": sum(1 for c in ranked_candidates if c["tier"] == "Potential Fit"),
        "Low Match": sum(1 for c in ranked_candidates if c["tier"] == "Low Match")
    }

    # Aggregate skill gap frequency
    missing_skill_counts: Dict[str, int] = {}
    for c in ranked_candidates:
        missing_must = c["sub_scores"]["skills"].get("missing_must", [])
        for s in missing_must:
            missing_skill_counts[s] = missing_skill_counts.get(s, 0) + 1

    sorted_skill_gaps = sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "success": True,
        "job_criteria": {
            "title": parsed_jd["title"],
            "min_experience_years": parsed_jd["min_experience_years"],
            "education": parsed_jd["education"],
            "must_have_skills": parsed_jd["skills"]["must_have"],
            "good_to_have_skills": parsed_jd["skills"]["good_to_have"]
        },
        "total_screened": len(ranked_candidates),
        "analytics": {
            "average_score": avg_score,
            "top_score": max(scores) if scores else 0.0,
            "tier_distribution": tier_distribution,
            "most_common_skill_gaps": [{"skill": k, "missing_in_candidates": v} for k, v in sorted_skill_gaps[:5]]
        },
        "candidates": ranked_candidates
    }


@app.post("/api/screen-json")
async def screen_candidates_json(request: ScreeningRequest):
    """JSON screening endpoint used for sample testing or programmatic API calls."""
    if not request.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text is required.")

    resumes_input = request.resumes or SAMPLE_RESUMES
    parsed_jd = JobDescriptionParser.parse(request.jd_text)

    evaluated_list = []
    for item in resumes_input:
        filename = item.get("filename", "resume.txt")
        raw_text = item.get("text", "")
        if not raw_text.strip():
            continue

        cand_data = EntityExtractor.extract_all(raw_text, filename=filename)
        # Use provided candidate_name if present in sample
        if item.get("candidate_name"):
            cand_data["candidate_name"] = item["candidate_name"]

        evaluation = matcher.evaluate_candidate(
            candidate_data=cand_data,
            raw_resume_text=raw_text,
            jd_data=parsed_jd,
            weights=request.weights
        )

        if request.anonymize:
            evaluation["candidate_name"] = f"Candidate #{len(evaluated_list) + 1}"
            evaluation["contact"] = {
                "email": "[Protected for Blind Screening]",
                "phone": "[Protected for Blind Screening]",
                "linkedin": None,
                "github": None
            }

        evaluated_list.append(evaluation)

    ranked_candidates = matcher.rank_candidates(evaluated_list, min_threshold=request.min_threshold)

    scores = [c["final_score"] for c in ranked_candidates]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "success": True,
        "job_criteria": {
            "title": parsed_jd["title"],
            "min_experience_years": parsed_jd["min_experience_years"],
            "education": parsed_jd["education"],
            "must_have_skills": parsed_jd["skills"]["must_have"],
            "good_to_have_skills": parsed_jd["skills"]["good_to_have"]
        },
        "total_screened": len(ranked_candidates),
        "analytics": {
            "average_score": avg_score,
            "top_score": max(scores) if scores else 0.0,
            "tier_distribution": {
                "Strong Fit": sum(1 for c in ranked_candidates if c["tier"] == "Strong Fit"),
                "Moderate Fit": sum(1 for c in ranked_candidates if c["tier"] == "Moderate Fit"),
                "Potential Fit": sum(1 for c in ranked_candidates if c["tier"] == "Potential Fit"),
                "Low Match": sum(1 for c in ranked_candidates if c["tier"] == "Low Match")
            }
        },
        "candidates": ranked_candidates
    }


@app.post("/api/export-csv")
async def export_csv(payload: Dict[str, Any]):
    """Export ranked candidate list as downloadable CSV."""
    candidates = payload.get("candidates", [])
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidate data to export.")

    output = io.StringIO()
    # CSV Header
    output.write("Rank,Candidate Name,Final Score (%),Tier,Recommended Action,Skills Score (%),Semantic Score (%),Experience Score (%),Education Score (%),Matched Must-Have Skills,Missing Must-Have Skills\n")

    for c in candidates:
        rank = c.get("rank", "")
        name = f'"{c.get("candidate_name", "")}"'
        score = c.get("final_score", 0)
        tier = f'"{c.get("tier", "")}"'
        action = f'"{c.get("recommended_action", "")}"'

        sub = c.get("sub_scores", {})
        sk_score = sub.get("skills", {}).get("score", 0)
        sem_score = sub.get("semantic", {}).get("score", 0)
        exp_score = sub.get("experience", {}).get("score", 0)
        edu_score = sub.get("education", {}).get("score", 0)

        matched_skills = "; ".join(sub.get("skills", {}).get("matched_must", []))
        missing_skills = "; ".join(sub.get("skills", {}).get("missing_must", []))

        output.write(f'{rank},{name},{score},{tier},{action},{sk_score},{sem_score},{exp_score},{edu_score},"{matched_skills}","{missing_skills}"\n')

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_screening_report.csv"}
    )
