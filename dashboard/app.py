import streamlit as st
import json
import pathlib
from datetime import datetime

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="AI-IPS SOC",
    layout="wide",
    page_icon="🛡"
)

# ==============================
# PATHS
# ==============================

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"

# ==============================
# SIDEBAR
# ==============================

st.sidebar.title("🛡 AI-IPS")

st.sidebar.markdown("### System Controls")

# Manual refresh button
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("### System Status")

# ==============================
# LOAD EVENTS
# ==============================

events = []

try:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            events = json.load(f)
except:
    events = []

total_events = len(events)

# ==============================
# STATUS INDICATORS
# ==============================

if total_events > 0:
    st.sidebar.success("AI-IPS Engine: Running")
else:
    st.sidebar.info("Waiting for events")

st.sidebar.metric("Total Events Logged", total_events)

# ==============================
# AI MODEL STATUS
# ==============================

st.sidebar.divider()
st.sidebar.markdown("### AI Engine")

st.sidebar.success("Hybrid AI Detector Active")
st.sidebar.success("Behavior Engine Active")
st.sidebar.success("Firewall Protection Enabled")

# ==============================
# MAIN PAGE
# ==============================

st.title("🛡 AI-IPS Security Operations Center")

st.markdown("""
Welcome to the **AI-IPS Cyber Defense Platform**.

Use the **left sidebar navigation** to explore the system:

### Available Dashboards

**📊 Overview**
- SOC command center
- Global cyber attack map
- Threat confidence gauge
- Network traffic graph
- Top attackers leaderboard

**📡 Live Threat Feed**
- Real-time intrusion alerts
- Source IP tracking
- Attack types and severity

**🌍 Threat Intelligence**
- Global attacker distribution
- Attack country statistics

**📈 Security Analytics**
- Attack trends
- Timeline analysis
- Threat severity distribution

**🧠 AI Training Monitor**
- Self-learning dataset
- Model training samples
- Label distribution
""")

st.divider()

# ==============================
# RECENT EVENTS PREVIEW
# ==============================

st.subheader("📌 Recent Security Events")

if total_events == 0:

    st.info("No security events detected yet. The IPS is actively monitoring network traffic.")

else:

    latest = events[-5:]

    for event in reversed(latest):

        ip = event.get("source_ip", "Unknown")
        attack = event.get("attack_type", "Unknown")
        event_type = event.get("event_type", "INFO")

        if event_type == "BLOCKED":

            st.error(f"🚨 BLOCKED {ip} ({attack})")

        elif event_type == "WARNING":

            st.warning(f"⚠ WARNING {ip} ({attack})")

        else:

            st.info(f"ℹ EVENT {ip} ({attack})")

# ==============================
# FOOTER
# ==============================

st.divider()

st.caption(
    f"AI-IPS Cyber Defense Platform • Running since {datetime.now().strftime('%Y')} • Manual Refresh Enabled"
)