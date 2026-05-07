import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from extractor import extract_text_from_pdf, analyze_resume
from emailer import send_to_n8n

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Orchestrator AI",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .score-card { background: #1e1e2e; border-radius: 12px; padding: 20px; text-align: center; }
    .score-number { font-size: 3rem; font-weight: 700; }
    .tag { display: inline-block; padding: 4px 12px; border-radius: 20px;
           background: #3a3a5c; color: #ccc; margin: 3px; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/document.png", width=60)
    st.title("Resume Orchestrator")
    st.caption("AI-Powered · Gemini · n8n Automation")
    st.divider()
    job_description = st.text_area(
        "📋 Job Description (optional)",
        placeholder="Paste the JD here for match scoring...",
        height=180
    )
    recipient_email = st.text_input(
        "📧 Send report to",
        placeholder="hiring@company.com"
    )

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("📄 AI Resume Document Orchestrator")
st.caption("Upload a resume → Gemini extracts & scores → n8n sends the right email automatically")

uploaded_file = st.file_uploader(
    "Drop a resume PDF here",
    type=["pdf"],
    help="Supports multi-page PDFs"
)

if uploaded_file:
    with st.spinner("🤖 Gemini is reading the resume..."):
        text = extract_text_from_pdf(uploaded_file)
        data = analyze_resume(text, job_description)

    st.success(f"✅ Analysis complete for **{data.get('candidate_name', 'Candidate')}**")

    # ── Row 1: Score cards ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    fit_score = data.get("fit_score", 0)
    ats_score = data.get("ats_score", 0)

    with col1:
        st.metric("🎯 Fit Score", f"{fit_score}/100")
    with col2:
        st.metric("🤖 ATS Score", f"{ats_score}/100")
    with col3:
        st.metric("💼 Experience", f"{data.get('total_experience_years', 0)} yrs")
    with col4:
        verdict = data.get("fit_verdict", "Unknown")
        color = "🟢" if fit_score >= 80 else "🟡" if fit_score >= 50 else "🔴"
        st.metric("📌 Verdict", f"{color} {verdict}")

    st.divider()

    # ── Row 2: Profile + Skills ───────────────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.subheader("👤 Candidate Profile")
        contact = data.get("contact", {})
        st.write(f"**Name:** {data.get('candidate_name')}")
        st.write(f"**Email:** {contact.get('email', 'N/A')}")
        st.write(f"**Phone:** {contact.get('phone', 'N/A')}")
        st.write(f"**Location:** {contact.get('location', 'N/A')}")
        st.write(f"**LinkedIn:** {contact.get('linkedin', 'N/A')}")
        st.info(data.get("summary", ""))

        st.subheader("🎓 Education")
        for edu in data.get("education", []):
            st.write(f"• **{edu.get('degree')}** — {edu.get('institution')} ({edu.get('year')})")

    with right:
        st.subheader("🛠️ Skills Breakdown")
        skills = data.get("skills", {})

        # Radar chart
        categories = ["Technical", "Soft Skills", "Tools", "Experience", "ATS Fit"]
        values = [
            min(len(skills.get("technical", [])) * 8, 100),
            min(len(skills.get("soft", [])) * 12, 100),
            min(len(skills.get("tools", [])) * 10, 100),
            min(data.get("total_experience_years", 0) * 10, 100),
            ats_score
        ]
        fig = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(99,102,241,0.3)',
            line=dict(color='rgba(99,102,241,0.9)', width=2),
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False, height=300,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Skill tags
        for label, key in [("⚙️ Technical", "technical"), ("💡 Soft", "soft"), ("🔧 Tools", "tools")]:
            st.write(f"**{label}:**")
            tags_html = " ".join(
                f'<span class="tag">{s}</span>'
                for s in skills.get(key, [])
            )
            st.markdown(tags_html, unsafe_allow_html=True)

    st.divider()

    # ── Row 3: Experience + Strengths/Gaps ───────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("💼 Work Experience")
        for exp in data.get("experience", []):
            with st.expander(f"**{exp.get('role')}** @ {exp.get('company')} ({exp.get('duration')})"):
                for h in exp.get("highlights", []):
                    st.write(f"• {h}")

    with col_b:
        st.subheader("✅ Strengths")
        for s in data.get("strengths", []):
            st.success(f"✓ {s}")

        st.subheader("⚠️ Gaps & Risks")
        for g in data.get("gaps", []):
            st.warning(f"⚡ {g}")

    st.divider()

    # ── Row 4: Recommendations + n8n trigger ─────────────────────────────────
    st.subheader("💡 AI Recommendations")
    for rec in data.get("recommendations", []):
        st.info(f"→ {rec}")

    st.divider()
    st.subheader("📬 Automated Email via n8n")

    score_color = (
        "🟢 Strong candidate — shortlist email will be sent to hiring manager."
        if fit_score >= 80 else
        "🟡 Moderate match — review email will be sent to HR team."
        if fit_score >= 50 else
        "🔴 Low fit — polite decline email will be triggered."
    )
    st.info(score_color)

    if st.button("🚀 Send Report via n8n", type="primary", use_container_width=True):
        if not recipient_email:
            st.error("Please enter a recipient email in the sidebar.")
        else:
            with st.spinner("Triggering n8n workflow..."):
                success = send_to_n8n(data, recipient_email)
            if success:
                st.success("✅ n8n workflow triggered! Email is on its way.")
                st.balloons()
            else:
                st.error("❌ Failed to reach n8n. Check that your webhook URL is active.")