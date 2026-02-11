import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document

# ==========================================================
#  Environment Setup
# ==========================================================
# Load .env for local development; Lightsail provides env vars directly
load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Demo sample files
SAMPLE_JOB_DESC_PATH = os.path.join("tests", "test-job-description.docx")
SAMPLE_RESUME_PATH = os.path.join("tests", "test-resume.docx")

# ==========================================================
#  Initialize OpenAI Client
# ==========================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "❌ OPENAI_API_KEY is not set. "
        "For local dev: create a .env file with your API key.\n"
        "For production: add OPENAI_API_KEY in Lightsail container environment variables."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================================
#  Helper Functions
# ==========================================================
def extract_text_from_file(filepath):
    """Extract text from a PDF or DOCX file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext == ".pdf":
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


def generate_match_response(job_description, resume_text):
    """Call OpenAI API to compare resume and job description."""
    prompt = f"""
You are a career assistant. A job description and a resume are provided.
Return a clear, bullet-point comparison of how well the resume matches or does not match the job description.
Use phrases like "✔️ Matches" and "❌ Missing" to explain each point.

Job Description:
{job_description}

Resume:
{resume_text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating match response: {e}"

# ==========================================================
#  Routes
# ==========================================================
@app.route("/", methods=["GET", "POST"])
def index():
    match_report = None
    error = None
    job_desc_value = ""
    active_tab = "description"

    if request.method == "POST":
        try:
            job_desc_value = (request.form.get("job_desc") or "").strip()
            resume_file = request.files.get("resume_file")

            # After any POST (success or error), keep the user on the Demo tab
            active_tab = "demo"

            if not job_desc_value or not resume_file or not resume_file.filename:
                error = "Please provide both a job description and a resume file."
            else:
                filename = secure_filename(resume_file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                resume_file.save(filepath)

                resume_text = extract_text_from_file(filepath)
                match_report = generate_match_response(job_desc_value, resume_text)

        except Exception as e:
            error = f"⚠️ {str(e)}"

    # Pass job_desc back so textarea can retain content (minimal UI change)
    return render_template(
        "index.html",
        match_report=match_report,
        error=error,
        job_desc=job_desc_value,
        demo_mode=False,
        active_tab=active_tab,
    )


@app.route("/demo", methods=["POST"])
def demo():
    """
    One-click demo:
    - Uses tests/test-job-description.docx
    - Uses tests/test-resume.docx
    - Runs analysis and renders index.html with the same UI/animations
    """
    try:
        job_desc_value = extract_text_from_file(SAMPLE_JOB_DESC_PATH)
        resume_text = extract_text_from_file(SAMPLE_RESUME_PATH)
        match_report = generate_match_response(job_desc_value, resume_text)

        return render_template(
            "index.html",
            match_report=match_report,
            error=None,
            job_desc=job_desc_value,
            demo_mode=True,
            active_tab="demo",
        )
    except Exception as e:
        return render_template(
            "index.html",
            match_report=None,
            error=f"⚠️ Demo failed: {str(e)}",
            job_desc="",
            demo_mode=False,
            active_tab="demo",
        )

# ==========================================================
#  Entry Point
# ==========================================================
if __name__ == "__main__":
    # Only used in development; Lightsail runs with Gunicorn
    print("✅ Starting Flask development server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
