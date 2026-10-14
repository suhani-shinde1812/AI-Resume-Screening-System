import os
import sys

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.parsers.doc_parser import DocumentParser
from backend.nlp.entity_extractor import EntityExtractor
from backend.nlp.jd_parser import JobDescriptionParser
from backend.nlp.matcher import MatcherEngine
from backend.utils.sample_data import SAMPLE_JDS, SAMPLE_RESUMES

def run_tests():
    print("=== TEST 1: Job Description Parsing ===")
    jd_raw = SAMPLE_JDS["ai_ml_engineer"]["description"]
    parsed_jd = JobDescriptionParser.parse(jd_raw)
    print(f"Title: {parsed_jd['title']}")
    print(f"Min Experience Required: {parsed_jd['min_experience_years']} years")
    print(f"Education Required: {parsed_jd['education']['required_degree']}")
    print(f"Must-Have Skills ({len(parsed_jd['skills']['must_have'])}): {parsed_jd['skills']['must_have']}")
    print(f"Good-to-Have Skills ({len(parsed_jd['skills']['good_to_have'])}): {parsed_jd['skills']['good_to_have']}")
    assert len(parsed_jd["skills"]["must_have"]) > 0, "Must have skills should not be empty"

    print("\n=== TEST 2: Resume Entity Extraction ===")
    sample_res = SAMPLE_RESUMES[0]
    entities = EntityExtractor.extract_all(sample_res["text"], sample_res["filename"])
    print(f"Candidate: {entities['candidate_name']}")
    print(f"Email: {entities['contact']['email']}")
    print(f"Experience: {entities['experience']['years']} yrs ({entities['experience']['seniority_level']})")
    print(f"Education: {entities['education']['highest_degree']}")
    print(f"Skills Found ({entities['skills']['total_count']}): {entities['skills']['all_skills'][:6]}...")
    assert entities["skills"]["total_count"] > 5, "Should extract skills"

    print("\n=== TEST 3: Candidate Scoring & Explainable AI ===")
    matcher = MatcherEngine()
    print(f"Sklearn loaded: {matcher.has_sklearn}")
    eval_result = matcher.evaluate_candidate(entities, sample_res["text"], parsed_jd)
    print(f"Final Score: {eval_result['final_score']}% | Tier: {eval_result['tier']}")
    print(f"Recommendation: {eval_result['recommended_action']}")
    print(f"Matched Must-Haves: {eval_result['sub_scores']['skills']['matched_must']}")
    print(f"Strengths: {eval_result['strengths']}")
    assert eval_result["final_score"] >= 70.0, "Senior AI Engineer candidate should score high on AI role"

    print("\n=== TEST 4: Batch Ranking across 5 candidates ===")
    batch_evals = []
    for cand in SAMPLE_RESUMES:
        c_entities = EntityExtractor.extract_all(cand["text"], cand["filename"])
        if cand.get("candidate_name"):
            c_entities["candidate_name"] = cand["candidate_name"]
        ev = matcher.evaluate_candidate(c_entities, cand["text"], parsed_jd)
        batch_evals.append(ev)

    ranked = matcher.rank_candidates(batch_evals)
    for c in ranked:
        print(f"Rank #{c['rank']}: {c['candidate_name']} — {c['final_score']}% ({c['tier']})")

    assert ranked[0]["candidate_name"] == "Aarav Sharma", "Aarav Sharma should rank #1 for AI role"

    print("\n=== TEST 5: PDF Parser Test ===")
    pdf_path = os.path.join("samples", "resumes", "Aarav_Sharma_Senior_AI_Engineer.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_text = DocumentParser.extract_text_from_pdf(f.read())
        print(f"Extracted {len(pdf_text)} chars from PDF. Sample: {pdf_text[:100]}...")
        assert len(pdf_text) > 50, "PDF extraction should succeed"

    print("\nALL TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_tests()
