import pandas as pd
import re

categories = {
    "Online Platform": ["online platform", "plataforma en línea", "virtual campus"],
    "Mentors and Teachers": ["mentor", "profesor", "teacher", "instructor", "docente"],
    "Price": ["price", "cost", "affordable", "precio", "costo"],
    "Career Support": ["career", "job", "empleo", "bolsa de trabajo"],
    "Content and Syllabus": ["course", "syllabus", "curriculum", "temario", "contenido"],
    "Job Guarantee": ["job guarantee", "garantía de empleo"],
    "Full Stack": ["full stack", "frontend", "backend"],
    "Cybersecurity": ["cybersecurity", "ciberseguridad"],
    "Data Science": ["data science", "ciencia de datos"],
    "Applied AI": ["applied ai", "inteligencia artificial aplicada"],
    "Outcomes": ["outcome", "resultados", "empleo obtenido"],
    "Scholarships": ["scholarship", "beca"],
    "Rigobot": ["rigobot"],
    "LearnPack": ["learnpack"]
}

def categorize_review(text):
    text_lower = text.lower()
    matched = []
    for category, keywords in categories.items():
        if any(re.search(r"\b" + re.escape(k) + r"\b", text_lower) for k in keywords):
            matched.append(category)
    return matched

df = pd.read_csv("reviews.csv")
df["combined_text"] = df["headline"].fillna("") + " " + df["review_body"].fillna("")
df["categories"] = df["combined_text"].apply(categorize_review)




