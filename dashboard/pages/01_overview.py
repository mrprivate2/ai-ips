import streamlit as st
import pandas as pd
import json
import pathlib
import plotly.graph_objects as go
import plotly.express as px

from utils.packet_rate import packet_rate_graph
from utils.threat_map import build_attack_map
from utils.leaderboard import top_attackers

st.set_page_config(
    layout="wide",
    page_title="AI-IPS Overview"
)

st.title("🛡 AI-IPS Security Operations Center")

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"

# =================================
# LOAD EVENTS
# =================================

events = []

try:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            events = json.load(f)
except:
    events = []

df = pd.DataFrame(events)

if not df.empty and "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])

# =================================
# METRICS
# =================================

total = len(df)

blocked = (
    len(df[df["event_type"] == "BLOCKED"])
    if not df.empty and "event_type" in df
    else 0
)

warnings = (
    len(df[df["event_type"] == "WARNING"])
    if not df.empty and "event_type" in df
    else 0
)

normal = total - blocked - warnings

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Events", total)
m2.metric("Blocked Attacks", blocked)
m3.metric("Warnings", warnings)
m4.metric("Normal Traffic", max(normal, 0))

st.divider()

# =================================
# AI THREAT GAUGE
# =================================

st.subheader("🧠 AI Threat Confidence")

confidence_score = 0

if total > 0:
    confidence_score = min(blocked / total, 1)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=confidence_score * 100,
    number={'suffix': "%"},
    title={'text': "Threat Level"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#ff4b4b"},
        'steps': [
            {'range': [0, 40], 'color': "#2ecc71"},
            {'range': [40, 70], 'color': "#f1c40f"},
            {'range': [70, 100], 'color': "#e74c3c"}
        ]
    }
))

st.plotly_chart(fig_gauge, width="stretch")

st.divider()

# =================================
# NETWORK TRAFFIC RATE
# =================================

st.subheader("📡 Network Traffic Rate")

fig_rate = packet_rate_graph(df)

if fig_rate:
    st.plotly_chart(fig_rate, width="stretch")
else:
    st.info("Waiting for network traffic data...")

st.divider()

# =================================
# GLOBAL ATTACK MAP
# =================================

st.subheader("🌍 Global Attack Map")

fig_map = build_attack_map(df)

if fig_map:
    st.plotly_chart(fig_map, width="stretch")
else:
    st.info("No attack sources detected yet.")

st.divider()

# =================================
# TOP ATTACKERS
# =================================

st.subheader("🔥 Top Attackers")

leaderboard = top_attackers(df)

if leaderboard is not None and not leaderboard.empty:

    st.dataframe(
        leaderboard,
        width="stretch",
        height=300
    )

else:

    st.info("No attackers detected yet.")

st.divider()

# =================================
# ATTACK TIMELINE
# =================================

st.subheader("📈 Attack Timeline")

if not df.empty and "timestamp" in df.columns:

    timeline = (
        df.groupby(pd.Grouper(key="timestamp", freq="1Min"))
        .size()
        .reset_index(name="events")
    )

    fig_time = px.line(
        timeline,
        x="timestamp",
        y="events",
        template="plotly_dark",
        title="Events Per Minute"
    )

    st.plotly_chart(fig_time, width="stretch")

else:

    st.info("Timeline will appear once events are recorded.")

st.divider()

# =================================
# LIVE ALERTS
# =================================

st.subheader("⚡ Live Alerts")

if not df.empty:

    latest = df.sort_values("timestamp", ascending=False).head(10)

    for _, row in latest.iterrows():

        ip = row.get("source_ip", "Unknown")
        attack = row.get("attack_type", "Unknown")
        event = row.get("event_type", "")

        if event == "BLOCKED":

            st.error(f"🚨 BLOCKED {ip} ({attack})")

        elif event == "WARNING":

            st.warning(f"⚠ WARNING {ip} ({attack})")

        else:

            st.info(f"ℹ EVENT {ip} ({attack})")

else:

    st.info("No threats detected yet. Monitoring network traffic...")