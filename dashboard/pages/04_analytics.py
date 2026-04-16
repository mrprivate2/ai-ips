import streamlit as st
import pandas as pd
import json
import pathlib
import plotly.express as px
from datetime import timedelta

st.set_page_config(layout="wide", page_title="AI IPS Analytics")

st.title("🛡️ AI Intrusion Prevention System - Analytics Dashboard")


# =============================
# LOAD DATA (SAFE)
# =============================

@st.cache_data(ttl=5)
def load_data():
    BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
    LOG_FILE = BASE_DIR / "logs" / "security_events.json"

    try:
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                return pd.DataFrame(json.load(f))
    except Exception as e:
        st.error(f"Error loading logs: {e}")

    return pd.DataFrame()


df = load_data()


# =============================
# EMPTY STATE
# =============================

if df.empty:
    st.warning("🚫 No security events yet. Start your IPS engine.")
    st.stop()


# =============================
# PREPROCESS
# =============================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df = df.sort_values("timestamp")


# =============================
# SIDEBAR FILTERS
# =============================

st.sidebar.subheader("🔍 Filters")

if "timestamp" in df.columns:

    min_time = df["timestamp"].min().to_pydatetime()
    max_time = df["timestamp"].max().to_pydatetime()

    start_default = max_time - timedelta(hours=1)
    if start_default < min_time:
        start_default = min_time

    time_range = st.sidebar.slider(
        "Time Range",
        min_value=min_time,
        max_value=max_time,
        value=(start_default, max_time),
    )

    df = df[
        (df["timestamp"] >= time_range[0]) &
        (df["timestamp"] <= time_range[1])
    ]

if "attack_type" in df.columns:
    selected_attacks = st.sidebar.multiselect(
        "Attack Type",
        options=df["attack_type"].unique(),
        default=df["attack_type"].unique(),
    )
    df = df[df["attack_type"].isin(selected_attacks)]

if "risk_level" in df.columns:
    selected_severity = st.sidebar.multiselect(
        "Severity",
        options=df["risk_level"].unique(),
        default=df["risk_level"].unique(),
    )
    df = df[df["risk_level"].isin(selected_severity)]


# =============================
# METRICS (REALISTIC)
# =============================

total = len(df)
blocked = len(df[df["event_type"] == "BLOCKED"]) if "event_type" in df else 0
warnings = len(df[df["event_type"] == "WARNING"]) if "event_type" in df else 0
unique_ips = df["source_ip"].nunique() if "source_ip" in df else 0
unknown = len(df[df["attack_type"] == "UNKNOWN_THREAT"]) if "attack_type" in df else 0

attack_rate = 0
if "timestamp" in df.columns:
    duration = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 60
    if duration > 0:
        attack_rate = round(total / duration, 2)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📊 Total", total)
col2.metric("🚫 Blocked", blocked)
col3.metric("⚠ Warnings", warnings)
col4.metric("🔥 Unique IPs", unique_ips)
col5.metric("🧠 Unknown Threats", unknown)

st.caption(f"⚡ Attack Rate: {attack_rate} events/min")

st.divider()


# =============================
# DISTRIBUTIONS
# =============================

if "attack_type" in df.columns:

    colA, colB = st.columns(2)

    with colA:
        st.subheader("📊 Attack Type Distribution")

        fig1 = px.pie(
            df,
            names="attack_type",
            template="plotly_dark",
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)

    with colB:
        st.subheader("⚠ Severity Distribution")

        fig2 = px.histogram(
            df,
            x="risk_level",
            color="risk_level",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

st.divider()


# =============================
# TOP ATTACKERS
# =============================

if "source_ip" in df.columns:

    st.subheader("🔥 Top Attackers")

    top_ips = (
        df.groupby("source_ip")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="count")
    )

    fig3 = px.bar(
        top_ips,
        x="source_ip",
        y="count",
        text="count",
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

st.divider()


# =============================
# TIMELINE + ANOMALY SPIKES
# =============================

if "timestamp" in df.columns:

    st.subheader("📈 Attack Timeline (Behavior Spikes)")

    timeline = (
        df.groupby(pd.Grouper(key="timestamp", freq="1Min"))
        .size()
        .reset_index(name="events")
    )

    threshold = timeline["events"].mean() + 2 * timeline["events"].std()
    timeline["spike"] = timeline["events"] > threshold

    fig4 = px.line(
        timeline,
        x="timestamp",
        y="events",
        markers=True,
        template="plotly_dark"
    )

    spikes = timeline[timeline["spike"]]

    fig4.add_scatter(
        x=spikes["timestamp"],
        y=spikes["events"],
        mode="markers",
        marker=dict(size=10, color="red"),
        name="Traffic Spike"
    )

    st.plotly_chart(fig4, use_container_width=True)

st.divider()


# =============================
# EXPORT
# =============================

st.subheader("⬇ Export Logs")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="security_events.csv",
    mime="text/csv",
)