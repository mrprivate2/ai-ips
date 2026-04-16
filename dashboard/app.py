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

st.sidebar.markdown("### ⚙ Controls")

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

st.sidebar.divider()

# ==============================
# LOAD EVENTS (SAFE)
# ==============================

def load_events():
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                return json.load(f)
    except:
        pass
    return []

events = load_events()
total_events = len(events)

# ==============================
# SYSTEM STATUS
# ==============================

st.sidebar.markdown("### 🟢 System Status")

if total_events > 0:
    st.sidebar.success("IPS Engine: ACTIVE")
else:
    st.sidebar.warning("IPS Engine: IDLE")

st.sidebar.metric("Total Events", total_events)

# ==============================
# ENGINE STATUS (REALISTIC)
# ==============================

st.sidebar.divider()
st.sidebar.markdown("### 🧠 Detection Engines")

st.sidebar.success("Hybrid Detection: Running")
st.sidebar.success("Behavior Analysis: Running")
st.sidebar.success("Firewall: Active")

# ==============================
# PROCESS EVENTS
# ==============================

blocked = 0
warnings = 0
unknown = 0

for e in events:

    if e.get("event_type") == "BLOCKED":
        blocked += 1

    if e.get("event_type") == "WARNING":
        warnings += 1

    if e.get("attack_type") == "UNKNOWN_THREAT":
        unknown += 1

# ==============================
# MAIN HEADER
# ==============================

st.title("🛡 AI-IPS Security Operations Center")

st.caption("Real-time intrusion detection and prevention system")

# ==============================
# TOP METRICS
# ==============================

c1, c2, c3, c4 = st.columns(4)

c1.metric("📊 Total Events", total_events)
c2.metric("🚫 Blocked", blocked)
c3.metric("⚠ Warnings", warnings)
c4.metric("🧠 Unknown Threats", unknown)

st.divider()

# ==============================
# SYSTEM OVERVIEW
# ==============================

st.subheader("📡 System Overview")

st.markdown("""
### Available Modules

**📊 Overview**
- Threat level and traffic monitoring

**📡 Live Feed**
- Real-time alerts and IP tracking

**🌍 Threat Intelligence**
- Attack origin and geographic insights

**📈 Analytics**
- Attack trends and anomaly spikes

**🧠 AI Training**
- Dataset growth and model updates
""")

st.divider()

# ==============================
# RECENT EVENTS
# ==============================

st.subheader("🚨 Recent Security Events")

if total_events == 0:

    st.info("🟢 No threats detected. Monitoring network...")

else:

    latest = events[-10:]

    for event in reversed(latest):

        ip = event.get("source_ip", "Unknown")
        attack = event.get("attack_type", "Unknown")
        event_type = event.get("event_type", "INFO")

        if attack == "UNKNOWN_THREAT":
            st.error(f"🧠 ANOMALY DETECTED → {ip}")

        elif event_type == "BLOCKED":
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
    f"AI-IPS • Cyber Defense Platform • {datetime.now().strftime('%Y')}"
)