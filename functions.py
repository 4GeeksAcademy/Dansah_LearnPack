import pandas as pd
import re
import unicodedata

categories = {
    "OnlinePlatform": ["online platform", "plataforma en línea", "virtual campus", "streaming", "plataforma online", "cloud", "plataforma"],
    "MentorsTeachers": ["mentor", "profesor", "teacher", "instructor", "docente", "mentors", "tutors", "teachers", "instructors", "profes", "mentores", "tutores", "profesores"],
    "Price": ["price", "cost", "affordable", "precio", "costo", "tuition", "cheap", "investment", "worth", "matrícula", "barato", "inversión", "vale la pena"],
    "CareerSupport": ["career", "job", "empleo", "bolsa de trabajo", "career support", "job search", "interview", "resume", "LinkedIn", "networking", "búsqueda de empleo", "entrevistas", "currículum", "apoyo laboral", "asesoría"],
    "ContentSyllabus": ["course", "syllabus", "curriculum", "temario", "contenido", "bootcamp", "program", "projects", "exercises", "learning", "knowledge", "classes", "clases", "proyectos", "ejercicios", "aprendizaje", "conocimientos"],
    "Job Guarantee": ["job guarantee", "garantía de empleo", "job placement", "empleo garantizado", "colocación laboral"],
    "FullStack": ["full stack", "frontend", "backend", "fullstack", "desarrollo full stack", "web development", "desarrollo web"],
    "Cybersecurity": ["cybersecurity", "ciberseguridad"],
    "DataScience": ["data science", "ciencia de datos", "machine learning", "ai", "inteligencia artificial"],
    "AppliedAI": ["applied ai", "inteligencia artificial aplicada", "ai program", "machine learning"],
    "Outcomes": ["outcome", "resultados", "empleo obtenido", "results", "success", "achieve", "goals", "exitos", "logros", "metas"],
    "Scholarships": ["scholarship", "beca", "financial aid", "ayuda financiera"],
    "Rigobot": ["rigobot"],
    "LearnPack": ["learnpack"]
}

# def categorize_review(headline=None, body=None):
#     # Ensure we have strings and handle NaN/None gracefully
#     headline_text = str(headline).lower() if pd.notna(headline) else ""
#     body_text = str(body).lower() if pd.notna(body) else ""
    
#     combined_text = f"{headline_text} {body_text}".strip()
    
#     matched = []
#     for category, keywords in categories.items():
#         if any(re.search(r"\b" + re.escape(k) + r"\b", combined_text) for k in keywords):
#             matched.append(category.replace(" ", "_"))  # replace spaces with underscores
    
#     return "_".join(matched) if matched else ""

def normalize_text(text):
    """Lowercase, remove accents, and strip extra spaces."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.strip()

def categorize_review(headline=None, body=None):
    """Return 1/0 per category for a review."""
    combined_text = f"{normalize_text(headline)} {normalize_text(body)}"
    result = {}
    for category, keywords in categories.items():
        result[category] = int(any(re.search(r"\b" + re.escape(normalize_text(k)) + r"\b", combined_text) for k in keywords))
    return result








