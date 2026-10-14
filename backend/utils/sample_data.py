"""
Pre-configured Sample Job Descriptions and Resumes for Instant Testing and Demonstrations.
"""

from typing import Dict, List

SAMPLE_JDS: Dict[str, Dict[str, str]] = {
    "ai_ml_engineer": {
        "title": "Senior AI / Machine Learning Engineer",
        "description": """Job Title: Senior AI / Machine Learning Engineer
Department: Artificial Intelligence & Data Platform
Location: Remote / Hybrid
Experience: 4+ years of relevant experience in Machine Learning and NLP.
Education: Bachelor's or Master's in Computer Science, Data Science, or related STEM field.

About the Role:
We are looking for an experienced Senior AI / Machine Learning Engineer to design, build, and deploy production-grade NLP, Large Language Model (LLM), and Generative AI applications. You will collaborate with engineering teams to integrate modern AI pipelines into our enterprise platform.

Requirements (Must Have):
- 4+ years of hands-on experience in Machine Learning and Natural Language Processing (NLP).
- Strong proficiency in Python, PyTorch or TensorFlow, and Scikit-Learn.
- Experience building RAG pipelines, fine-tuning LLMs, and working with Hugging Face transformers.
- Experience with Vector Databases (such as Pinecone, FAISS, ChromaDB, or Qdrant).
- Solid knowledge of Git, Docker, and REST APIs (FastAPI or Flask).

Nice to Have (Good to Have):
- Experience deploying ML models on AWS (SageMaker, Lambda, ECS) or Azure.
- Hands-on experience with LangChain or LlamaIndex.
- Familiarity with CI/CD pipelines, Kubernetes, and MLOps tools (MLflow, Weights & Biases).
- Master's or Ph.D. degree in a quantitative domain."""
    },
    "fullstack_dev": {
        "title": "Full-Stack Python & React Developer",
        "description": """Job Title: Full-Stack Python & React Developer
Location: Hybrid
Experience: 3+ years of professional software development experience.
Education: Bachelor's Degree in Computer Science or equivalent.

Job Overview:
We are seeking a versatile Full-Stack Engineer skilled in building modern web applications with Python backends and React frontends.

Key Requirements (Must Have):
- 3+ years of experience in Python web development using FastAPI or Django.
- Strong proficiency with React, TypeScript or JavaScript, and modern CSS/Tailwind.
- Experience with relational databases like PostgreSQL and ORMs (SQLAlchemy, Prisma).
- Proven track record of developing and consuming RESTful APIs.
- Experience using Git and Docker containerization.

Preferred Qualifications (Good to Have):
- Familiarity with Redis caching and Celery task queues.
- Basic experience with AWS cloud services (S3, EC2).
- Unit testing with Pytest and Jest."""
    },
    "data_analyst": {
        "title": "Junior to Mid Data Analyst",
        "description": """Job Title: Data Analyst
Location: On-site / Hybrid
Experience: 1-2 years of data analysis or business intelligence experience.
Education: Bachelor's in Statistics, Mathematics, Computer Science, or Business.

Core Requirements (Must Have):
- Strong proficiency in SQL for querying large relational databases.
- Practical experience with Python (Pandas, NumPy, Matplotlib, Seaborn).
- Experience building interactive dashboards in PowerBI or Tableau.
- Solid understanding of exploratory data analysis and descriptive statistics.

Nice to Have:
- Basic understanding of machine learning algorithms (Scikit-Learn).
- Experience with Excel advanced formulas and ETL workflows."""
    }
}

SAMPLE_RESUMES: List[Dict[str, str]] = [
    {
        "filename": "Aarav_Sharma_Senior_AI_Engineer.txt",
        "candidate_name": "Aarav Sharma",
        "text": """Aarav Sharma
Email: aarav.sharma.ai@example.com | Phone: (555) 234-5678
LinkedIn: linkedin.com/in/aarav-sharma-ml | GitHub: github.com/aarav-sharma

PROFESSIONAL SUMMARY:
Lead AI Engineer with 5+ years of extensive experience architecting state-of-the-art Deep Learning, NLP, and Generative AI systems. Proven record of developing Retrieval-Augmented Generation (RAG) pipelines, fine-tuning LLMs, and deploying scalable microservices to AWS cloud.

CORE SKILLS:
- Languages & Core: Python, C++, SQL, Git, Linux
- AI / ML / NLP: Machine Learning, Deep Learning, Natural Language Processing, NLP, PyTorch, Scikit-Learn, Transformers, Hugging Face, LLM, Generative AI, RAG, BERT, LangChain
- Vector Databases: FAISS, ChromaDB, Pinecone
- Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD, FastAPI, Flask, REST APIs

PROFESSIONAL EXPERIENCE:
Senior AI Engineer | NeuralScale Technologies (2021 - Present)
- Designed and deployed enterprise RAG pipeline serving 200k daily queries with sub-second latency using FastAPI and Pinecone.
- Fine-tuned open-source Hugging Face transformer models (Llama and Mistral) for domain-specific contract extraction with 94% precision.
- Built automated model evaluation and MLOps workflows using PyTorch, Docker, and GitHub Actions on AWS.

Machine Learning Engineer | Apex Data Labs (2019 - 2021)
- Developed NLP classification models using Scikit-Learn and BERT for automated customer feedback triage.
- Engineered ETL pipelines with Pandas and PostgreSQL, reducing processing overhead by 40%.

EDUCATION:
- Master of Science in Computer Science (Artificial Intelligence specialization) | Stanford University (2017 - 2019)
- Bachelor of Technology in Computer Science | Indian Institute of Technology (2013 - 2017)"""
    },
    {
        "filename": "Priya_Patel_ML_Engineer.txt",
        "candidate_name": "Priya Patel",
        "text": """Priya Patel
Email: priya.patel.dev@example.com | Phone: (555) 876-5432
LinkedIn: linkedin.com/in/priya-patel-data | GitHub: github.com/priyapatel

SUMMARY:
Data Scientist & Machine Learning Engineer with 3.5 years of industry experience building predictive models, NLP classifiers, and data analysis pipelines using Python, Scikit-Learn, TensorFlow, and SQL.

SKILLS:
- Languages: Python, SQL, R, Bash
- Machine Learning & Data: Machine Learning, Scikit-Learn, TensorFlow, Keras, Pandas, NumPy, NLP, Matplotlib, Data Analysis, Feature Engineering
- Frameworks & Tools: Flask, FastAPI, Git, Docker, Postman, PostgreSQL
- Cloud: Basic AWS, S3

WORK EXPERIENCE:
Machine Learning Engineer | Innovate Analytics (2021 - Present)
- Built NLP text summarization and sentiment analysis tools using Python, TensorFlow, and Scikit-Learn.
- Deployed predictive REST APIs using FastAPI and Docker.
- Collaborated with product teams to clean and analyze datasets of over 5M user records with Pandas.

Junior Data Analyst | TechCorp (2020 - 2021)
- Wrote complex SQL queries on PostgreSQL for business intelligence reports.
- Developed dashboards and exploratory data analysis scripts.

EDUCATION:
- Bachelor of Engineering in Information Technology | Mumbai University (2016 - 2020)"""
    },
    {
        "filename": "Rohan_Verma_FullStack_Dev.txt",
        "candidate_name": "Rohan Verma",
        "text": """Rohan Verma
Email: rohan.verma.code@example.com | Phone: (555) 432-1098
GitHub: github.com/rohan-verma-fullstack

PROFESSIONAL SUMMARY:
Full Stack Developer with 4 years of experience building modern web applications, scalable REST APIs, and microservices using React, Node.js, Python, and PostgreSQL.

TECHNICAL SKILLS:
- Frontend: React, JavaScript, TypeScript, Next.js, HTML, CSS, TailwindCSS, Redux
- Backend: Python, FastAPI, Django, Node.js, Express, REST APIs
- Databases: PostgreSQL, MongoDB, Redis, SQLAlchemy
- DevOps & Tools: Docker, Git, GitHub Actions, AWS (EC2, S3), Nginx

PROFESSIONAL EXPERIENCE:
Full Stack Software Engineer | CloudStack Solutions (2021 - Present)
- Developed responsive web interfaces using React, TypeScript, and TailwindCSS.
- Architected robust backend services in Python FastAPI and PostgreSQL.
- Implemented asynchronous tasks with Celery and Redis.

Web Developer | WebCraft Studios (2020 - 2021)
- Built client web apps with React, JavaScript, and Node.js.
- Integrated payment gateways and external third-party REST APIs.

EDUCATION:
- Bachelor of Technology in Computer Science | Delhi Technological University (2016 - 2020)"""
    },
    {
        "filename": "Sneha_Kulkarni_Fresher_Data_Analyst.txt",
        "candidate_name": "Sneha Kulkarni",
        "text": """Sneha Kulkarni
Email: sneha.kulkarni@example.com | Phone: (555) 345-6789
LinkedIn: linkedin.com/in/sneha-kulkarni-data

OBJECTIVE:
Enthusiastic Recent Computer Science Graduate seeking an entry-level Data Analyst or Junior ML role. Strong foundation in Python, SQL, Statistics, and foundational Machine Learning.

SKILLS:
- Technical Skills: Python, SQL, Pandas, NumPy, Matplotlib, Seaborn, Scikit-Learn, Git
- BI & Tools: Tableau, Excel, PowerBI, Jupyter Notebooks
- Soft Skills: Problem Solving, Critical Thinking, Presentation, Teamwork

PROJECTS:
- Customer Churn Prediction: Built a binary classifier using Scikit-Learn and Pandas on Kaggle dataset, achieving 82% ROC-AUC.
- E-Commerce Sales Dashboard: Created an interactive Tableau dashboard visualizing quarterly sales metrics.
- Sentiment Analysis on Movie Reviews: Implemented basic NLP bag-of-words and TF-IDF models in Python.

EDUCATION:
- Bachelor of Science in Statistics & Data Science | Pune University (2021 - 2024)
- GPA: 3.8 / 4.0"""
    },
    {
        "filename": "Marcus_Chen_DevOps_Cloud.txt",
        "candidate_name": "Marcus Chen",
        "text": """Marcus Chen
Email: marcus.chen.cloud@example.com | Phone: (555) 901-2345
GitHub: github.com/marcuschen-devops

PROFESSIONAL SUMMARY:
DevOps and Cloud Infrastructure Engineer with 6+ years of experience designing secure, highly-available infrastructure on AWS and Kubernetes.

TECHNICAL COMPETENCIES:
- Cloud Platforms: AWS, Azure, GCP
- Containerization & Orchestration: Docker, Kubernetes, Helm, Terraform, Ansible
- CI/CD & Monitoring: Jenkins, GitLab CI, GitHub Actions, Prometheus, Grafana, ELK Stack
- Scripting & Automation: Bash, Python, Linux, Shell

WORK EXPERIENCE:
Lead DevOps Engineer | SkyHigh Networks (2020 - Present)
- Managed multi-region Kubernetes clusters on AWS EKS serving millions of requests.
- Automated infrastructure deployment with Terraform and Ansible.
- Reduced deployment cycle times by 65% through optimized CI/CD pipelines.

Systems Administrator | CoreTech Solutions (2018 - 2020)
- Administered Linux production servers, Nginx load balancers, and PostgreSQL databases.

EDUCATION:
- Bachelor of Science in Information Technology | University of Texas (2014 - 2018)"""
    }
]
