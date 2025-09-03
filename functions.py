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

def pull_reviews(df, review):
    
    review_df = df[[review, "OnlinePlatform", "MentorsTeachers", "Price", "MentorsTeachers"
    "Price","CareerSupport", "ContentSyllabus", "Job Guarantee", "FullStack", "Cybersecurity", 
    "DataScience","AppliedAI", "Outcomes", "Scholarships", "Rigobot", "LearnPack"]]

    review_df.columns.values[0] = 'Review'

    return  review_df


def concat_dataframes(df_list:list):
    full_data = pd.concat(df_list, axis=0)

    return full_data







