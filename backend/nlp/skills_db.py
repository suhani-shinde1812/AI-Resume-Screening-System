"""
Comprehensive Skills Taxonomy for Resume and Job Description Analysis.
Categorized into domains to support granular matching, radar charts, and domain gap analysis.
"""

from typing import Dict, List, Set

SKILL_CATEGORIES: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "dart", "matlab",
        "perl", "shell", "bash", "powershell", "sql", "html", "css", "sass", "less"
    ],
    "Web & Frontend Frameworks": [
        "react", "react.js", "reactjs", "angular", "angularjs", "vue", "vue.js", "vuejs",
        "next.js", "nextjs", "nuxt.js", "svelte", "sveltekit", "jquery", "tailwind",
        "tailwindcss", "bootstrap", "material-ui", "mui", "chakra-ui", "redux", "zustand",
        "mobx", "webpack", "vite", "babel", "graphql", "rest api", "restful api", "websockets"
    ],
    "Backend & Microservices": [
        "node.js", "nodejs", "express", "express.js", "fastapi", "flask", "django",
        "spring", "spring boot", "asp.net", ".net core", "ruby on rails", "laravel",
        "gin", "fiber", "nest.js", "nestjs", "grpc", "microservices", "celery",
        "rabbit mq", "rabbitmq", "apache kafka", "kafka", "redis"
    ],
    "AI, ML & Data Science": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "llm", "large language models", "generative ai", "genai",
        "rag", "retrieval-augmented generation", "transformers", "bert", "gpt",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "opencv",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "spacy", "nltk",
        "hugging face", "huggingface", "langchain", "llamaindex", "xgboost",
        "lightgbm", "catboost", "data analysis", "data mining", "data science",
        "data engineering", "feature engineering", "model training", "fine-tuning",
        "vector database", "chromadb", "faiss", "pinecone", "qdrant", "weaviate"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp", "google cloud",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "gitlab ci",
        "github actions", "ci/cd", "continuous integration", "helm", "linux", "unix",
        "nginx", "apache", "prometheus", "grafana", "elk stack", "cloudformation",
        "serverless", "aws lambda", "cloud architecture"
    ],
    "Databases & Big Data": [
        "postgresql", "postgres", "mysql", "mongodb", "sqlite", "oracle", "sql server",
        "redis", "cassandra", "elasticsearch", "neo4j", "dynamodb", "mariadb",
        "snowflake", "bigquery", "apache spark", "spark", "hadoop", "hive",
        "dbt", "airflow", "apache airflow", "etl", "data warehouse", "prisma", "sqlalchemy"
    ],
    "Mobile Development": [
        "android", "ios", "react native", "flutter", "swiftui", "jetpack compose",
        "xamarin", "ionic", "cordova"
    ],
    "Testing & Quality Assurance": [
        "unit testing", "pytest", "unittest", "jest", "mocha", "chai", "cypress",
        "selenium", "playwright", "postman", "jmeter", "test automation", "tdd", "bdd"
    ],
    "Methodologies & Tools": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "trello",
        "agile", "scrum", "kanban", "devops", "sdlc", "system design",
        "object-oriented programming", "oop", "clean architecture", "design patterns"
    ],
    "Soft Skills & Management": [
        "communication", "team leadership", "problem solving", "critical thinking",
        "collaboration", "adaptability", "time management", "project management",
        "mentorship", "presentation", "cross-functional collaboration"
    ]
}

# Flattened set for quick O(1) membership checks
ALL_SKILLS: Set[str] = set()
SKILL_TO_CATEGORY: Dict[str, str] = {}
SKILL_CANONICAL_MAP: Dict[str, str] = {}

# Canonical aliases map
ALIASES: Dict[str, List[str]] = {
    "react": ["react.js", "reactjs"],
    "node.js": ["nodejs", "node js", "node"],
    "next.js": ["nextjs", "next js"],
    "vue": ["vue.js", "vuejs"],
    "angular": ["angularjs", "angular.js"],
    "fastapi": ["fast api"],
    "spring boot": ["springboot"],
    "postgresql": ["postgres", "pgsql"],
    "mongodb": ["mongo"],
    "scikit-learn": ["sklearn"],
    "amazon web services": ["aws"],
    "google cloud platform": ["gcp", "google cloud"],
    "microsoft azure": ["azure"],
    "kubernetes": ["k8s"],
    "natural language processing": ["nlp"],
    "large language models": ["llm", "llms"],
    "generative ai": ["genai", "gen ai"],
    "retrieval-augmented generation": ["rag"],
    "docker": ["containerization"],
    "continuous integration": ["ci/cd", "ci cd"],
    "apache kafka": ["kafka"],
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "artificial intelligence": ["ai"],
    "golang": ["go language", "go lang"]
}

for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        canonical = skill.lower().strip()
        ALL_SKILLS.add(canonical)
        SKILL_TO_CATEGORY[canonical] = category
        SKILL_CANONICAL_MAP[canonical] = canonical

for canonical_target, alias_list in ALIASES.items():
    cat = SKILL_TO_CATEGORY.get(canonical_target, "Methodologies & Tools")
    ALL_SKILLS.add(canonical_target)
    SKILL_TO_CATEGORY[canonical_target] = cat
    for alias in alias_list:
        alias_clean = alias.lower().strip()
        ALL_SKILLS.add(alias_clean)
        SKILL_CANONICAL_MAP[alias_clean] = canonical_target
        SKILL_TO_CATEGORY[alias_clean] = cat


def get_canonical_skill(skill: str) -> str:
    """Normalize a skill name to its canonical representation."""
    cleaned = skill.lower().strip()
    return SKILL_CANONICAL_MAP.get(cleaned, cleaned)


def get_category_for_skill(skill: str) -> str:
    """Return the category for a given skill or 'Other Technical'."""
    canonical = get_canonical_skill(skill)
    return SKILL_TO_CATEGORY.get(canonical, "Other Technical")
