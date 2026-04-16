import streamlit as st
import pandas as pd
import json
import pathlib

st.set_page_config(layout="wide")

st.title("📡 Live Threat Feed")

BASE_DIR = pathlib.Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "logs" / "security_events.json"


# ============================
# SIDEBAR CONTROLS
# ============================

st.sidebar.title("⚙ Controls")

show_only_blocked = st.sidebar.checkbox("🚨 Show Only Blocked", value=False)


# ============================
# REFRESH BUTTON
# ============================

col1, col2 = st.columns([1, 6])

with col1:
    if st.button("🔄 Refresh Feed"):
        st.rerun()


# ============================
# LOAD EVENTS (SAFE)
# ============================

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


# ============================
# EMPTY STATE
# ============================

if df.empty:
    st.info("🟢 AI-IPS is monitoring network traffic.\n\nNo threats detected yet.")

else:

    # ============================
    # PREPROCESS
    # ============================

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values("timestamp", ascending=False)


    # ============================
    # FILTERS
    # ============================

    search_ip = st.text_input("🔍 Search by IP")

    if search_ip and "source_ip" in df.columns:
        df = df[df["source_ip"].astype(str).str.contains(search_ip, na=False)]

    if show_only_blocked and "event_type" in df.columns:
        df = df[df["event_type"] == "BLOCKED"]


    # ============================
    # METRICS (REALISTIC)
    # ============================

    total = len(df)
    blocked = len(df[df["event_type"] == "BLOCKED"]) if "event_type" in df else 0
    warnings = len(df[df["event_type"] == "WARNING"]) if "event_type" in df else 0
    unknown = len(df[df["attack_type"] == "UNKNOWN_THREAT"]) if "attack_type" in df else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Events", total)
    c2.metric("Blocked", blocked)
    c3.metric("Warnings", warnings)
    c4.metric("🧠 Unknown Threats", unknown)

    st.divider()


    # ============================
    # STATUS FORMAT
    # ============================

    def format_event(row):

        attack = row.get("attack_type", "")
        event = row.get("event_type", "")

        if attack == "UNKNOWN_THREAT":
            return "🧠 ANOMALY"

        if event == "BLOCKED":
            return "🚨 BLOCKED"

        elif event == "WARNING":
            return "⚠ WARNING"

        return "ℹ NORMAL"

    df["status"] = df.apply(format_event, axis=1)


    # ============================
    # COLOR STYLING
    # ============================

    def highlight_row(row):

        attack = row.get("attack_type", "")
        event = row.get("event_type", "")

        if attack == "UNKNOWN_THREAT":
            return ["background-color: #4a0000"] * len(row)

        if event == "BLOCKED":
            return ["background-color: #330000"] * len(row)

        elif event == "WARNING":
            return ["background-color: #3d2f00"] * len(row)

        return [""] * len(row)


    # ============================
    # COLUMN ORDER (SAFE)
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
        df.style.apply(highlight_row, axis=1),
        use_container_width=True,
        height=650
    )