import requests, os
from dotenv import load_dotenv

load_dotenv()

def send_to_n8n(analysis: dict, recipient_email: str):
    """
    Push resume analysis to n8n webhook.
    n8n will route the email based on fit_score.
    """
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    payload = {
        "candidate_name": analysis.get("candidate_name"),
        "fit_score":       analysis.get("fit_score", 0),
        "fit_verdict":     analysis.get("fit_verdict"),
        "ats_score":       analysis.get("ats_score", 0),
        "strengths":       analysis.get("strengths", []),
        "gaps":            analysis.get("gaps", []),
        "recommendations": analysis.get("recommendations", []),
        "total_experience": analysis.get("total_experience_years", 0),
        "skills_technical": analysis.get("skills", {}).get("technical", []),
        "recipient_email": recipient_email,
        "summary":         analysis.get("summary", ""),
    }

    response = requests.post(webhook_url, json=payload, timeout=10)
    return response.status_code == 200