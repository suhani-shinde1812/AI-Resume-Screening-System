"""
Generates sample resumes in .txt and .pdf format for physical file upload testing.
"""

import os
from backend.utils.sample_data import SAMPLE_JDS, SAMPLE_RESUMES

def generate_samples():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jds_dir = os.path.join(base_dir, "samples", "jds")
    resumes_dir = os.path.join(base_dir, "samples", "resumes")

    os.makedirs(jds_dir, exist_ok=True)
    os.makedirs(resumes_dir, exist_ok=True)

    # 1. Write sample JDs as .txt
    for key, data in SAMPLE_JDS.items():
        file_path = os.path.join(jds_dir, f"{key}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data["description"])
        print(f"Created JD: {file_path}")

    # 2. Write sample resumes as .txt
    for cand in SAMPLE_RESUMES:
        file_path = os.path.join(resumes_dir, cand["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cand["text"])
        print(f"Created Resume TXT: {file_path}")

    # 3. Create a PDF resume using ReportLab for Aarav Sharma
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = os.path.join(resumes_dir, "Aarav_Sharma_Senior_AI_Engineer.pdf")
        c = canvas.Canvas(pdf_path, pagesize=letter)
        y = 750

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Aarav Sharma - Senior AI Engineer")
        y -= 25

        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Email: aarav.sharma.ai@example.com | Phone: (555) 234-5678 | GitHub: github.com/aarav-sharma")
        y -= 20

        c.line(50, y, 550, y)
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "PROFESSIONAL SUMMARY")
        y -= 18

        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Lead AI Engineer with 5+ years building RAG pipelines, fine-tuning LLMs, and deploying to AWS.")
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "CORE SKILLS")
        y -= 18

        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Python, Machine Learning, Deep Learning, Natural Language Processing, NLP, PyTorch, Scikit-Learn,")
        y -= 15
        c.drawString(50, y, "Transformers, Hugging Face, LLM, Generative AI, RAG, FAISS, Pinecone, AWS, Docker, Kubernetes, FastAPI.")
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "EXPERIENCE")
        y -= 18

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Senior AI Engineer | NeuralScale Technologies (2021 - Present)")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, "- Architected high-throughput RAG search using FastAPI, Pinecone, and Hugging Face.")
        y -= 15
        c.drawString(60, y, "- Deployed containerized microservices to AWS using Docker and CI/CD pipelines.")
        y -= 20

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Machine Learning Engineer | Apex Data Labs (2019 - 2021)")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, "- Trained NLP classification models with Scikit-Learn and BERT.")
        y -= 25

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "EDUCATION")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Master of Science in Computer Science | Stanford University (2017 - 2019)")
        y -= 15
        c.drawString(50, y, "Bachelor of Technology in Computer Science | IIT (2013 - 2017)")

        c.save()
        print(f"Created Resume PDF: {pdf_path}")
    except Exception as e:
        print(f"Reportlab PDF creation skipped: {e}")

if __name__ == "__main__":
    generate_samples()
