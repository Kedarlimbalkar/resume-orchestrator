# 📄 Resume Orchestrator AI

An AI-powered resume screening dashboard that extracts, scores, and analyzes resumes using **Groq (Llama/GPT-OSS)**, then automatically routes candidate emails through an **n8n** workflow based on fit score — no manual triggering required.

## How It Works

1. Upload a resume PDF (and optionally a job description) via the Streamlit UI.
2. `extractor.py` pulls text from the PDF and sends it to Groq's LLM, which returns a structured analysis: candidate profile, skills, experience, fit score, ATS score, strengths, gaps, and recommendations.
3. The dashboard displays this analysis with score cards, a skills radar chart, and a detailed breakdown.
4. On clicking **"Send Report via n8n"**, `emailer.py` POSTs the analysis to an n8n webhook.
5. n8n routes the notification automatically based on `fit_score`:
   - **≥ 80** → Shortlist email to hiring manager
   - **50–79** → Review email to HR team
   - **< 50** → Polite decline email to candidate

## Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI/LLM:** [Groq API](https://groq.com/) (`openai/gpt-oss-120b`)
- **PDF Parsing:** PyMuPDF (`fitz`)
- **Visualization:** Plotly
- **Automation:** [n8n](https://n8n.io/) (Cloud or self-hosted)

## Project Structure

```
├── app.py              # Streamlit UI and main app logic
├── extractor.py         # PDF text extraction + Groq LLM analysis
├── emailer.py            # Sends analysis payload to n8n webhook
├── requirements.txt     # Python dependencies
├── .env                  # API keys and webhook URL (not committed)
└── .gitignore
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Kedarlimbalkar/resume-orchestrator.git
cd resume-orchestrator
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
N8N_WEBHOOK_URL=https://your-instance.app.n8n.cloud/webhook/resume-orchestrator
```
> Get a Groq API key at [console.groq.com](https://console.groq.com/keys).
> Never commit this file — it's excluded via `.gitignore`.

### 5. Set up the n8n workflow
1. Create an n8n instance (Cloud or self-hosted).
2. Build a workflow: **Webhook** (POST) → **Switch** (routing on `fit_score`) → **Send Email** nodes for shortlist/review/decline branches.
3. Activate the workflow.
4. Copy the **Production URL** into `N8N_WEBHOOK_URL` in your `.env`.

### 6. Run the app
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

## Usage

1. Upload a resume PDF.
2. (Optional) Paste a job description for match-scoring against a specific role.
3. Enter a recipient email in the sidebar.
4. Review the AI-generated analysis.
5. Click **Send Report via n8n** — the appropriate email is sent automatically, with no manual step in n8n.

## Security Notes

- API keys and webhook URLs live only in `.env`, which is git-ignored.
- If a key is ever accidentally exposed (e.g., committed to a public repo), rotate it immediately from the provider's console (Groq, Google AI Studio) — assume it's compromised the moment it's public.

## License

Personal project — not currently licensed for reuse.
