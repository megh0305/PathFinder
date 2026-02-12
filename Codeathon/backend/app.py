import os
from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
from docx import Document

# -------------------------------
# CONFIG
# -------------------------------
UPLOAD_FOLDER = "../uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_result = {}   # used by /result route

# -------------------------------
# APP INIT
# -------------------------------
app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

# -------------------------------
# HELPER: EXTRACT RESUME TEXT
# -------------------------------
def extract_text_from_resume(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + " "

    return text.lower()

# -------------------------------
# HOME PAGE
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------
# 1️⃣ Future-You Career Simulator
# -------------------------------
@app.route("/future-career", methods=["POST"])
def future_career():
    global latest_result
    data = request.json
    exp = data.get("experience", "Student")

    if exp == "Student":
        y1, y3, y5 = "Junior Analyst", "Data Scientist", "Senior AI Engineer"
    else:
        y1, y3, y5 = "Data Analyst", "Senior Data Scientist", "AI Lead"

    latest_result = {
        "year_1": y1,
        "year_3": y3,
        "year_5": y5,
        "salary": "₹6 – 18 LPA",
        "linkedin_profile": "AI-driven professional with strong analytics and problem-solving skills."
    }

    return jsonify(latest_result)

# -------------------------------
# 3️⃣ Skill Gap Analyzer
# -------------------------------
@app.route("/skill-gap", methods=["POST"])
def skill_gap():
    data = request.json

    # Normalize skills
    raw_skills = data.get("skills", [])
    current_skills = [
        skill.strip().lower()
        for skill in raw_skills
        if skill.strip() != ""
    ]

    target_role = data.get("target_role", "").lower()

    ROLE_SKILLS = {
        "data scientist": [
            "python", "sql", "statistics",
            "machine learning", "data visualization"
        ],
        "software engineer": [
            "python", "data structures", "algorithms",
            "git", "object oriented programming"
        ],
        "ai engineer": [
            "python", "machine learning",
            "deep learning", "linear algebra"
        ],
        "web developer": [
            "html", "css", "javascript",
            "backend framework", "databases"
        ]
    }

    required_skills = ROLE_SKILLS.get(
        target_role,
        ["problem solving", "programming basics", "communication"]
    )

    missing_skills = [
        skill.title()
        for skill in required_skills
        if skill not in current_skills
    ]

    roadmap = {
        "Month 1": [f"Learn fundamentals of {skill}" for skill in missing_skills[:2]],
        "Month 2": [f"Build mini projects using {skill}" for skill in missing_skills[2:4]],
        "Month 3": [
            "Build a capstone project",
            "Practice interview questions",
            "Revise concepts"
        ]
    }

    return jsonify({
        "missing_skills": missing_skills,
        "roadmap": roadmap
    })

# -------------------------------
# RESULT PAGE
# -------------------------------
@app.route("/result")
def result():
    return render_template("result.html", data=latest_result)

# -------------------------------
# PAGES
# -------------------------------
@app.route("/future")
def future_page():
    return render_template("future.html")

@app.route("/skillgap")
def skillgap_page():
    return render_template("skillgap.html")

@app.route("/resume")
def resume_page():
    return render_template("resume.html")

# -------------------------------
# RESUME ANALYSIS + ATS
# -------------------------------
@app.route("/resume-analysis", methods=["POST"])
def resume_analysis():
    file = request.files.get("resume_file")
    target_role = request.form.get("role", "").lower()

    if not file or file.filename == "":
        return jsonify({"error": "No resume uploaded"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    resume_text = extract_text_from_resume(file_path)

    if resume_text.strip() == "":
        return jsonify({
            "ats_score": 0,
            "matched_keywords": [],
            "missing_keywords": ["Unable to read resume text"],
            "suggestions": [
                "Upload a text-based PDF or DOCX",
                "Avoid scanned image resumes"
            ]
        })

    ROLE_KEYWORDS = {
        "data scientist": ["python", "sql", "machine learning", "statistics", "pandas", "numpy"],
        "software engineer": ["python", "java", "data structures", "algorithms", "git"],
        "web developer": ["html", "css", "javascript", "react", "backend"]
    }

    keywords = ROLE_KEYWORDS.get(
        target_role,
        ["problem solving", "communication", "teamwork"]
    )

    matched = [k for k in keywords if k in resume_text]
    missing = [k.title() for k in keywords if k not in resume_text]

    ats_score = int((len(matched) / len(keywords)) * 100)

    return jsonify({
        "ats_score": ats_score,
        "matched_keywords": [k.title() for k in matched],
        "missing_keywords": missing,
        "suggestions": [
            "Add more role-specific keywords",
            "Quantify achievements with numbers",
            "Use clear section headings",
            "Keep resume concise (1–2 pages)"
        ]
    })

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
