import streamlit as st
import requests
import json
from pathlib import Path
import time

st.set_page_config(page_title="HoneyPot Agentic AI", page_icon="🛡️", layout="wide")

# --------- Premium Theme ---------
st.markdown(
    """
<style>
:root {
  --green: #22c55e;
  --bg: #020617;
  --glass: rgba(15, 23, 42, 0.65);
  --border: rgba(148, 163, 184, 0.18);
  --shadow: 0 25px 60px rgba(0,0,0,.45);
  --muted: #9aa4b2;
}
body {
  background: radial-gradient(1200px 400px at 20% -10%, #064e3b 0%, #020617 55%);
}
.hero {
  backdrop-filter: blur(14px);
  background: linear-gradient(180deg, rgba(34,197,94,.14), rgba(2,6,23,.85));
  padding: 34px 40px;
  border-radius: 26px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}
.hero h1 {
  margin: 0;
  font-size: 40px;
  font-weight: 900;
  letter-spacing: .6px;
  color: var(--green);
}
.hero p { margin-top: 8px; color: var(--muted); }

.card {
  backdrop-filter: blur(12px);
  background: var(--glass);
  padding: 18px 22px;
  border-radius: 20px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  margin-bottom: 14px;
  transition: transform .18s ease, box-shadow .18s ease;
}
.card:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 30px 80px rgba(0,0,0,.55); }

.label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .1em; }
.kpi { font-size: 24px; font-weight: 900; }
.badge-high { color: #ef4444; font-weight: 900; }
.badge-medium { color: #f59e0b; font-weight: 900; }
.badge-low { color: #22c55e; font-weight: 900; }

button[kind="primary"] {
  border-radius: 16px !important;
  padding: 10px 16px !important;
  box-shadow: 0 12px 24px rgba(34,197,94,.35) !important;
}

.footer { color:#7c8aa5; font-size:12px; margin-top:22px; border-top:1px solid var(--border); padding-top:12px; }
</style>
""",
    unsafe_allow_html=True,
)

# --------- Header ---------
st.markdown(
    """
<div class="hero">
  <h1>HoneyPot Agentic AI</h1>
  <p>Enterprise-grade scam detection, threat intelligence extraction, and honeypot analytics</p>
</div>
""",
    unsafe_allow_html=True,
)

# --------- Preset Demo Buttons ---------
st.write("**Quick Test Scenarios**")
d1, d2, d3 = st.columns(3)
if d1.button("KYC Phishing"):
    st.session_state["msg"] = (
        "Urgent! Your SBI account has been blocked due to KYC issues. Verify now at https://secure-kyc-update.in"
    )
if d2.button("Lottery Scam"):
    st.session_state["msg"] = (
        "Congratulations! You have won a lottery prize. Click now to claim."
    )
if d3.button("Job Scam"):
    st.session_state["msg"] = (
        "We are hiring for part-time roles. Pay a small registration fee to get shortlisted."
    )

# --------- Layout ---------
left, right = st.columns([2, 3])

with left:
    st.subheader("Analyze Communication")
    message = st.text_area(
        "Enter message to analyze",
        height=170,
        key="msg",
        placeholder="Paste suspicious SMS, email, or chat message here…",
    )
    analyze = st.button("🚀 Analyze Threat", use_container_width=True)

with right:
    st.subheader("Threat Intelligence")
    result = st.container()

# --------- Call API ---------
if analyze:
    if not message.strip():
        st.warning("Please enter a message.")
    else:
        with st.spinner("Executing agentic AI pipeline…"):
            try:
                res = requests.post(
                    "http://127.0.0.1:8000/analyze-scam",
                    json={"message": message},
                    timeout=30,
                )
            except Exception:
                st.error(
                    "Backend not reachable. Please ensure the API server is running."
                )
                st.stop()

        if res.status_code == 200:
            data = res.json()
            conf = data.get("confidence", "Unknown")
            badge = (
                "badge-high"
                if conf == "High"
                else "badge-medium" if conf == "Medium" else "badge-low"
            )

            with result:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(
                        f"<div class='card'><div class='label'>Scam Category</div><div class='kpi'>{data['scam_type']}</div></div>",
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f"<div class='card'><div class='label'>Risk Score</div><div class='kpi'>{data['risk_score']}/100</div></div>",
                        unsafe_allow_html=True,
                    )
                with c3:
                    st.markdown(
                        f"<div class='card'><div class='label'>Confidence Level</div><div class='{badge} kpi'>{conf}</div></div>",
                        unsafe_allow_html=True,
                    )

                # Animated Risk Meter
                prog = st.progress(0)
                for i in range(min(data["risk_score"], 100) + 1):
                    prog.progress(i / 100)
                    time.sleep(0.005)

                st.markdown(
                    f"<div class='card'><div class='label'>Recommended Action</div><div class='kpi'>🛡️ {data['advice']}</div></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("### Extracted Threat Indicators")
                st.json(data["extracted_entities"])
        else:
            st.error("API error. Please review backend logs.")

# --------- Dashboard: Recent Activity + Mini Chart ---------
st.markdown("## 📊 Live Honeypot Activity")

log_path = Path("data/scam_logs.json")
if log_path.exists():
    logs = json.loads(log_path.read_text() or "[]")
    if logs:
        colA, colB = st.columns([2, 1])
        with colA:
            st.markdown("**Recent Events**")
            for item in logs[-5:][::-1]:
                st.write(
                    f"• **{item['timestamp']}** — {item['scam_type']} — Risk {item['risk_score']}"
                )
        with colB:
            risks = [x.get("risk_score", 0) for x in logs[-50:]]
            st.markdown("**Risk Distribution (last 50)**")
            st.bar_chart(risks)
    else:
        st.info("No honeypot events yet. Analyze messages to generate activity.")
else:
    st.info(
        "Log file not found. Honeypot logging will appear here once events are recorded."
    )

# --------- Footer ---------
st.markdown(
    """
<div class="footer">
  © 2026 HoneyPot Agentic AI • FastAPI + Hugging Face • Secure Intelligence Platform (Demo)
</div>
""",
    unsafe_allow_html=True,
)
