import pandas as pd
import re

categories = {
    "OnlinePlatform": ["online platform", "plataforma en línea", "virtual campus"],
    "MentorsTeachers": ["mentor", "profesor", "teacher", "instructor", "docente"],
    "Price": ["price", "cost", "affordable", "precio", "costo"],
    "CareerSupport": ["career", "job", "empleo", "bolsa de trabajo"],
    "ContentSyllabus": ["course", "syllabus", "curriculum", "temario", "contenido"],
    "Job Guarantee": ["job guarantee", "garantía de empleo"],
    "FullStack": ["full stack", "frontend", "backend"],
    "Cybersecurity": ["cybersecurity", "ciberseguridad"],
    "DataScience": ["data science", "ciencia de datos"],
    "AppliedAI": ["applied ai", "inteligencia artificial aplicada"],
    "Outcomes": ["outcome", "resultados", "empleo obtenido"],
    "Scholarships": ["scholarship", "beca"],
    "Rigobot": ["rigobot"],
    "LearnPack": ["learnpack"]
}

def categorize_review(headline=None, body=None):
    # Ensure we have strings and handle NaN/None gracefully
    headline_text = str(headline).lower() if pd.notna(headline) else ""
    body_text = str(body).lower() if pd.notna(body) else ""
    
    combined_text = f"{headline_text} {body_text}".strip()
    
    matched = []
    for category, keywords in categories.items():
        if any(re.search(r"\b" + re.escape(k) + r"\b", combined_text) for k in keywords):
            matched.append(category.replace(" ", "_"))  # replace spaces with underscores
    
    return "_".join(matched) if matched else ""








