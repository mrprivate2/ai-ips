import streamlit as st
import pandas as pd
import json
import pathlib
import plotly.graph_objects as go
import plotly.express as px

from utils.packet_rate import packet_rate_graph
from utils.threat_map import build_attack_map
from utils.leaderboard import top_attackers


# =============================
# CONFIG
# =============================

st.set_page_config(layout="wide", page_title="AI-IPS SOC Dashboard")
st.title("🛡 AI-IPS Security Operations Center")

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"


# =============================
# LOAD EVENTS (SAFE)
# =============================

def load_events():
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                return json.load(f)
    except:
        pass
    return []


events = load_events()
df = pd.DataFrame(events)

if not df.empty and "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])


# =============================
# FILTERS
# =============================

st.sidebar.subheader("🎯 Filters")

attack_options = ["ALL"]
if not df.empty and "attack_type" in df.columns:
    attack_options += sorted(df["attack_type"].dropna().unique().tolist())

attack_filter = st.sidebar.selectbox("Attack Type", attack_options)

if attack_filter != "ALL":
    df = df[df["attack_type"] == attack_filter]


# =============================
# METRICS
# =============================

total = len(df)

blocked = len(df[df["event_type"] == "BLOCKED"]) if not df.empty else 0
warnings = len(df[df["event_type"] == "WARNING"]) if not df.empty else 0
unknown = len(df[df["attack_type"] == "UNKNOWN_THREAT"]) if not df.empty else 0

normal = max(total - blocked - warnings, 0)

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Total Events", total)
m2.metric("Blocked", blocked)
m3.metric("Warnings", warnings)
m4.metric("Normal", normal)
m5.metric("🧠 Unknown Threats", unknown)

st.divider()


# =============================
# AI THREAT LEVEL (REALISTIC)
# =============================

st.subheader("🧠 AI Threat Level")

if total > 0:
    threat_score = (blocked * 1.0 + warnings * 0.5 + unknown * 1.2) / total
else:
    threat_score = 0

threat_score = min(threat_score, 1)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=threat_score * 100,
    number={'suffix': "%"},
    title={'text': "Threat Level"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#ff4b4b"},
        'steps': [
            {'range': [0, 30], 'color': "#2ecc71"},
            {'range': [30, 70], 'color': "#f1c40f"},
            {'range': [70, 100], 'color': "#e74c3c"}
        ]
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()


# =============================
# NETWORK TRAFFIC
# =============================

st.subheader("📡 Network Traffic Rate")

fig_rate = packet_rate_graph(df)
st.plotly_chart(fig_rate, use_container_width=True) if fig_rate else st.info("No data yet")

st.divider()


# =============================
# ATTACK MAP
# =============================

st.subheader("🌍 Global Attack Map")

fig_map = build_attack_map(df)
st.plotly_chart(fig_map, use_container_width=True) if fig_map else st.info("No attacks yet")

st.divider()


# =============================
# ATTACK DISTRIBUTION
# =============================

st.subheader("📊 Attack Distribution")

if not df.empty and "attack_type" in df.columns:

    attack_counts = df["attack_type"].value_counts().reset_index()
    attack_counts.columns = ["attack_type", "count"]

    fig_pie = px.pie(
        attack_counts,
        names="attack_type",
        values="count",
        template="plotly_dark"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.info("No attack data available.")

st.divider()


# =============================
# TOP ATTACKERS
# =============================

st.subheader("🔥 Top Attackers")

leaderboard = top_attackers(df)

if leaderboard is not None and not leaderboard.empty:
    st.dataframe(leaderboard, use_container_width=True, height=300)
else:
    st.info("No attackers yet.")

st.divider()


# =============================
# TIMELINE
# =============================

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
        template="plotly_dark"
    )

    st.plotly_chart(fig_time, use_container_width=True)

else:
    st.info("No timeline data yet.")

st.divider()


# =============================
# LIVE ALERTS (MEANINGFUL)
# =============================

st.subheader("⚡ Live Alerts")

if not df.empty:

    latest = df.sort_values("timestamp", ascending=False).head(10)

    for _, row in latest.iterrows():

        ip = row.get("source_ip", "Unknown")
        attack = row.get("attack_type", "Unknown")
        event = row.get("event_type", "")

        if attack == "UNKNOWN_THREAT":
            st.error(f"🧠 UNKNOWN THREAT: {ip}")

        elif event == "BLOCKED":
            st.error(f"🚨 BLOCKED {ip} ({attack})")

        elif event == "WARNING":
            st.warning(f"⚠ WARNING {ip} ({attack})")

        else:
            st.info(f"ℹ EVENT {ip} ({attack})")

else:
    st.info("Monitoring network...")