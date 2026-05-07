from groq import Groq
import fitz  # PyMuPDF
import json, os, re
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from uploaded PDF bytes."""
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def analyze_resume(text: str, job_description: str = "") -> dict:
    """Send resume text to Groq and get structured JSON back."""

    jd_section = f"""
    Job Description to match against:
    {job_description}
    """ if job_description else "No job description provided — do a general analysis."

    prompt = f"""
    You are an expert HR analyst and ATS (Applicant Tracking System).
    Analyze the resume below and return ONLY a valid JSON object.

    {jd_section}

    Resume Text:
    {text}

    Return this exact JSON structure (no markdown, no explanation, no backticks):
    {{
      "candidate_name": "Full Name",
      "contact": {{
        "email": "email or null",
        "phone": "phone or null",
        "linkedin": "url or null",
        "location": "city, country or null"
      }},
      "summary": "2-sentence professional summary",
      "skills": {{
        "technical": ["skill1", "skill2"],
        "soft": ["skill1", "skill2"],
        "tools": ["tool1", "tool2"]
      }},
      "experience": [
        {{
          "company": "Company Name",
          "role": "Job Title",
          "duration": "Jan 2022 - Present",
          "years": 2.5,
          "highlights": ["achievement1", "achievement2"]
        }}
      ],
      "education": [
        {{
          "degree": "B.Tech Computer Science",
          "institution": "University Name",
          "year": "2020",
          "gpa": "8.5/10 or null"
        }}
      ],
      "certifications": ["cert1", "cert2"],
      "languages": ["English", "Hindi"],
      "total_experience_years": 5.0,
      "fit_score": 78,
      "fit_verdict": "Strong Match",
      "strengths": ["strength1", "strength2", "strength3"],
      "gaps": ["gap1", "gap2"],
      "recommendations": ["rec1", "rec2", "rec3"],
      "keywords_matched": ["keyword1", "keyword2"],
      "ats_score": 82
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()

    # Clean any accidental markdown fences
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract JSON block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Groq returned invalid JSON. Raw output:\n" + raw)
