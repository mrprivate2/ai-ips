import streamlit as st
import pandas as pd
import json
import pathlib

st.set_page_config(layout="wide")

st.title("📡 Live Threat Feed")

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"

# ============================
# REFRESH BUTTON
# ============================

col1, col2 = st.columns([1, 6])

with col1:
    if st.button("🔄 Refresh Feed"):
        st.rerun()

# ============================
# LOAD EVENTS
# ============================

events = []

try:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            events = json.load(f)
except:
    events = []

df = pd.DataFrame(events)

# ============================
# EMPTY STATE
# ============================

if df.empty:

    st.info("🟢 AI-IPS is monitoring network traffic.\n\nNo threats detected yet.")

else:

    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Sort newest first
    df = df.sort_values("timestamp", ascending=False)

    # ============================
    # METRICS
    # ============================

    total = len(df)
    blocked = len(df[df["event_type"] == "BLOCKED"])
    warnings = len(df[df["event_type"] == "WARNING"])

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Events", total)
    c2.metric("Blocked", blocked)
    c3.metric("Warnings", warnings)

    st.divider()

    # ============================
    # SEARCH FILTER
    # ============================

    search_ip = st.text_input("🔍 Search by IP")

    if search_ip:
        df = df[df["source_ip"].str.contains(search_ip, na=False)]

    # ============================
    # STATUS FORMAT
    # ============================

    def format_event(event):

        if event == "BLOCKED":
            return "🚨 BLOCKED"

        elif event == "WARNING":
            return "⚠ WARNING"

        return event

    if "event_type" in df.columns:
        df["status"] = df["event_type"].apply(format_event)

    # ============================
    # COLUMN ORDER
    # ============================

    preferred_columns = [
        "timestamp",
        "status",
        "source_ip",
        "attack_type",
        "risk_level"
    ]

    columns = [c for c in preferred_columns if c in df.columns]

    if columns:
        df = df[columns]

    # ============================
    # DISPLAY TABLE
    # ============================

    st.dataframe(
        df,
        width="stretch",
        height=650
    )