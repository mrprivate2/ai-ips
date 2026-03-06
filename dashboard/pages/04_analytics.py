import streamlit as st
import pandas as pd
import json
import pathlib
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 Security Analytics")

# =============================
# MANUAL REFRESH
# =============================

if st.button("🔄 Refresh Analytics"):
    st.rerun()

# =============================
# LOAD EVENTS
# =============================

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"

events = []

try:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            events = json.load(f)
except:
    pass

df = pd.DataFrame(events)

# =============================
# EMPTY STATE
# =============================

if df.empty:

    st.info("No analytics data available yet.")

    st.subheader("Attack Type Distribution")
    st.info("Waiting for attack data...")

    st.subheader("Top Attack Sources")
    st.info("Waiting for attack data...")

    st.subheader("Attack Timeline")
    st.info("Waiting for attack data...")

    st.subheader("Severity Distribution")
    st.info("Waiting for attack data...")

    st.stop()

# =============================
# PREPARE DATA
# =============================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])

# =============================
# SUMMARY METRICS
# =============================

total = len(df)
blocked = len(df[df["event_type"] == "BLOCKED"]) if "event_type" in df else 0
warnings = len(df[df["event_type"] == "WARNING"]) if "event_type" in df else 0

c1, c2, c3 = st.columns(3)

c1.metric("Total Events", total)
c2.metric("Blocked Attacks", blocked)
c3.metric("Warnings", warnings)

st.divider()

# =============================
# ATTACK TYPE DISTRIBUTION
# =============================

if "attack_type" in df.columns:

    st.subheader("📊 Attack Type Distribution")

    attack_counts = df["attack_type"].value_counts()

    fig1 = px.pie(
        values=attack_counts.values,
        names=attack_counts.index,
        template="plotly_dark",
    )

    st.plotly_chart(fig1, width="stretch")

st.divider()

# =============================
# TOP ATTACKING IPS
# =============================

if "source_ip" in df.columns:

    st.subheader("🔥 Top Attack Sources")

    top_ips = (
        df.groupby("source_ip")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        x=top_ips.index,
        y=top_ips.values,
        labels={"x": "Source IP", "y": "Attack Count"},
        template="plotly_dark",
    )

    st.plotly_chart(fig2, width="stretch")

st.divider()

# =============================
# ATTACK TIMELINE
# =============================

if "timestamp" in df.columns:

    st.subheader("📈 Attack Timeline")

    timeline = (
        df.groupby(pd.Grouper(key="timestamp", freq="1Min"))
        .size()
        .reset_index(name="events")
    )

    fig3 = px.line(
        timeline,
        x="timestamp",
        y="events",
        template="plotly_dark",
    )

    st.plotly_chart(fig3, width="stretch")

st.divider()

# =============================
# SEVERITY DISTRIBUTION
# =============================

if "risk_level" in df.columns:

    st.subheader("⚠ Threat Severity Distribution")

    severity = df["risk_level"].value_counts()

    fig4 = px.bar(
        x=severity.index,
        y=severity.values,
        labels={"x": "Risk Level", "y": "Events"},
        template="plotly_dark",
    )

    st.plotly_chart(fig4, width="stretch")