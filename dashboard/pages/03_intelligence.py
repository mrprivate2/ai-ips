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


# =============================
# LOAD DATA (SAFE)
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


# =============================
# EMPTY STATE
# =============================

if df.empty:
    st.info("Waiting for security events...")

    fig = go.Figure()
    fig.update_layout(
        geo=dict(showland=True, landcolor="rgb(25,25,25)", bgcolor="black"),
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.stop()


# =============================
# PREPARE DATA
# =============================

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

if "source_ip" not in df.columns:
    st.error("No source IP data available.")
    st.stop()


# =============================
# GEOLOCATION (CACHED)
# =============================

@st.cache_data(ttl=3600)
def get_ip_location(ip):
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,lat,lon",
            timeout=2
        )
        data = r.json()

        if data.get("lat"):
            return data["lat"], data["lon"], data["country"]

    except:
        pass

    return None, None, "Unknown"


# =============================
# BUILD MAP DATA (OPTIMIZED)
# =============================

attackers = []

grouped = df.groupby("source_ip")

for ip, group in grouped:

    lat, lon, country = get_ip_location(ip)

    if lat is None:
        continue

    attack_count = len(group)

    has_anomaly = any(group["attack_type"] == "UNKNOWN_THREAT")

    attackers.append({
        "ip": ip,
        "lat": lat,
        "lon": lon,
        "country": country,
        "count": attack_count,
        "anomaly": has_anomaly
    })

map_df = pd.DataFrame(attackers)


# =============================
# TARGET SYSTEM (STATIC)
# =============================

target_lat = 28.6139
target_lon = 77.2090


# =============================
# CYBER ATTACK MAP
# =============================

st.subheader("🌍 Live Cyber Attack Map")

fig = go.Figure()

if not map_df.empty:

    sizes = map_df["count"].clip(1, 20)
    colors = map_df["anomaly"].map({True: "red", False: "orange"})

    fig.add_trace(go.Scattergeo(
        lon=map_df["lon"],
        lat=map_df["lat"],
        text=map_df["ip"],
        mode="markers",
        marker=dict(size=sizes, color=colors),
        name="Attack Sources"
    ))

    for _, row in map_df.iterrows():
        fig.add_trace(go.Scattergeo(
            lon=[row["lon"], target_lon],
            lat=[row["lat"], target_lat],
            mode="lines",
            line=dict(width=1, color="orange"),
            opacity=0.4,
            showlegend=False
        ))

fig.add_trace(go.Scattergeo(
    lon=[target_lon],
    lat=[target_lat],
    mode="markers",
    marker=dict(size=12, color="cyan"),
    name="Protected System"
))

fig.update_layout(
    geo=dict(showland=True, landcolor="rgb(30,30,30)", bgcolor="black"),
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()


# =============================
# TRAFFIC RATE
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

st.plotly_chart(fig2, use_container_width=True)

st.divider()


# =============================
# AI THREAT LEVEL (REALISTIC)
# =============================

st.subheader("🧠 Threat Level")

total = len(df)
blocked = len(df[df["event_type"] == "BLOCKED"])
warnings = len(df[df["event_type"] == "WARNING"])
unknown = len(df[df["attack_type"] == "UNKNOWN_THREAT"]) if "attack_type" in df else 0

score = (blocked * 1.0 + warnings * 0.5 + unknown * 1.2) / max(total, 1)
score = min(score, 1)

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score * 100,
    number={'suffix': "%"},
    title={'text': "Threat Level"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "red"},
        'steps': [
            {'range': [0, 30], 'color': "green"},
            {'range': [30, 70], 'color': "yellow"},
            {'range': [70, 100], 'color': "red"}
        ]
    }
))

st.plotly_chart(gauge, use_container_width=True)

st.divider()


# =============================
# TOP COUNTRIES
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

    st.plotly_chart(fig3, use_container_width=True)

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

st.plotly_chart(fig4, use_container_width=True)

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

    st.plotly_chart(fig5, use_container_width=True)