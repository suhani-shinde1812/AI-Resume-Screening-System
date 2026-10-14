"""
Main launcher script for TalentScan AI — Resume Screening & Decision Support System.
Runs the FastAPI web server on http://127.0.0.1:8000
"""

import sys
import os
import uvicorn

if __name__ == "__main__":
    # Ensure current directory is on PYTHONPATH
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print("=" * 70)
    print(" TalentScan AI — Intelligent Resume Screening System")
    print(" Decision-Support Engine for Recruiters & HR Teams")
    print("=" * 70)
    print(" Starting server at: http://127.0.0.1:8050")
    print(" Interactive Recruiter Dashboard: http://127.0.0.1:8050/")
    print(" OpenAPI Swagger Documentation:  http://127.0.0.1:8050/docs")
    print("=" * 70)

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8050, reload=True)
