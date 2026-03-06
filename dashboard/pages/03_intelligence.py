import streamlit as st
import pandas as pd
import json
import pathlib
import plotly.graph_objects as go
import plotly.express as px
import requests

st.set_page_config(layout="wide")

st.title("🌍 Global Threat Intelligence Center")

# =============================
# MANUAL REFRESH
# =============================

if st.button("🔄 Refresh Intelligence"):
    st.rerun()

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

    st.info("Waiting for security events...")

    fig = go.Figure()

    fig.update_layout(
        geo=dict(
            showland=True,
            landcolor="rgb(25,25,25)",
            bgcolor="black"
        ),
        template="plotly_dark"
    )

    st.plotly_chart(fig, width="stretch")

    st.stop()

# =============================
# PREPARE DATA
# =============================

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])

if "source_ip" not in df.columns:
    st.error("No source IP data available.")
    st.stop()

# =============================
# GEOLOCATION
# =============================

@st.cache_data(ttl=3600)
def get_ip_location(ip):

    try:

        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,lat,lon",
            timeout=3
        )

        data = r.json()

        if data.get("lat"):

            return data["lat"], data["lon"], data["country"]

    except:
        pass

    return None, None, "Unknown"


# =============================
# BUILD MAP DATA
# =============================

attackers = []

for ip in df["source_ip"].unique():

    lat, lon, country = get_ip_location(ip)

    if lat is None:
        continue

    attackers.append({
        "ip": ip,
        "lat": lat,
        "lon": lon,
        "country": country
    })

map_df = pd.DataFrame(attackers)

# Protected system location
target_lat = 28.6139
target_lon = 77.2090

# =============================
# CYBER ATTACK MAP
# =============================

st.subheader("🌍 Live Cyber Attack Map")

fig = go.Figure()

if not map_df.empty:

    fig.add_trace(go.Scattergeo(
        lon=map_df["lon"],
        lat=map_df["lat"],
        text=map_df["ip"],
        mode="markers",
        marker=dict(size=8, color="red"),
        name="Attack Sources"
    ))

    for _, row in map_df.iterrows():

        fig.add_trace(go.Scattergeo(
            lon=[row["lon"], target_lon],
            lat=[row["lat"], target_lat],
            mode="lines",
            line=dict(width=1, color="orange"),
            opacity=0.6,
            showlegend=False
        ))

# Target system
fig.add_trace(go.Scattergeo(
    lon=[target_lon],
    lat=[target_lat],
    mode="markers",
    marker=dict(size=12, color="cyan"),
    name="Protected System"
))

fig.update_layout(
    geo=dict(
        showland=True,
        landcolor="rgb(30,30,30)",
        bgcolor="black"
    ),
    template="plotly_dark"
)

st.plotly_chart(fig, width="stretch")

st.divider()

# =============================
# PACKET RATE GRAPH
# =============================

st.subheader("⚡ Network Traffic Rate")

traffic = (
    df.groupby(pd.Grouper(key="timestamp", freq="10s"))
    .size()
    .reset_index(name="events")
)

fig2 = px.line(
    traffic,
    x="timestamp",
    y="events",
    template="plotly_dark",
    title="Packets per 10 seconds"
)

st.plotly_chart(fig2, width="stretch")

st.divider()

# =============================
# THREAT CONFIDENCE GAUGE
# =============================

st.subheader("🧠 AI Threat Confidence")

total = len(df)
blocked = len(df[df["event_type"] == "BLOCKED"]) if "event_type" in df else 0

score = min(blocked / max(total, 1), 1)

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score * 100,
    title={'text': "Threat Level"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "red"},
        'steps': [
            {'range': [0, 40], 'color': "green"},
            {'range': [40, 70], 'color': "yellow"},
            {'range': [70, 100], 'color': "red"}
        ]
    }
))

st.plotly_chart(gauge, width="stretch")

st.divider()

# =============================
# TOP ATTACK COUNTRIES
# =============================

if not map_df.empty:

    st.subheader("🔥 Top Attacking Countries")

    country_counts = map_df["country"].value_counts().head(10)

    fig3 = px.bar(
        x=country_counts.index,
        y=country_counts.values,
        labels={"x": "Country", "y": "Attack Count"},
        template="plotly_dark"
    )

    st.plotly_chart(fig3, width="stretch")

st.divider()

# =============================
# TOP ATTACKERS
# =============================

st.subheader("🚨 Top Attacking IPs")

top_ips = (
    df.groupby("source_ip")
    .size()
    .sort_values(ascending=False)
    .head(10)
)

fig4 = px.bar(
    x=top_ips.index,
    y=top_ips.values,
    labels={"x": "Source IP", "y": "Attacks"},
    template="plotly_dark"
)

st.plotly_chart(fig4, width="stretch")

st.divider()

# =============================
# SEVERITY DISTRIBUTION
# =============================

if "risk_level" in df.columns:

    st.subheader("⚠ Threat Severity Distribution")

    severity = df["risk_level"].value_counts()

    fig5 = px.pie(
        values=severity.values,
        names=severity.index,
        template="plotly_dark"
    )

    st.plotly_chart(fig5, width="stretch")