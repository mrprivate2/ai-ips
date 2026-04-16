import pandas as pd
import plotly.graph_objects as go
import requests


# ======================================
# GEOLOCATION CACHE
# ======================================

geo_cache = {}


def get_ip_location(ip):

    if ip in geo_cache:
        return geo_cache[ip]

    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=country,lat,lon",
            timeout=2
        )
        data = r.json()

        lat = data.get("lat")
        lon = data.get("lon")
        country = data.get("country", "Unknown")

        if lat and lon:
            geo_cache[ip] = (lat, lon, country)
            return lat, lon, country

    except:
        pass

    geo_cache[ip] = (None, None, "Unknown")
    return None, None, "Unknown"


# ======================================
# BUILD ATTACK MAP
# ======================================

def build_attack_map(df):

    if df.empty or "source_ip" not in df.columns:
        return None

    attackers = []

    grouped = df.groupby("source_ip")

    for ip, group in grouped:

        lat, lon, country = get_ip_location(ip)

        if lat is None:
            continue

        count = len(group)

        # =========================
        # ANOMALY DETECTION
        # =========================

        has_anomaly = False
        if "attack_type" in group.columns:
            has_anomaly = any(group["attack_type"] == "UNKNOWN_THREAT")

        # =========================
        # SEVERITY LOGIC
        # =========================

        if has_anomaly:
            severity = "HIGH"
            color = "red"
        elif count > 20:
            severity = "MEDIUM"
            color = "orange"
        else:
            severity = "LOW"
            color = "green"

        attackers.append({
            "ip": ip,
            "lat": lat,
            "lon": lon,
            "country": country,
            "count": count,
            "color": color,
            "severity": severity
        })

    if not attackers:
        return None

    map_df = pd.DataFrame(attackers)

    # =========================
    # TARGET SYSTEM
    # =========================

    target_lat = 28.6139
    target_lon = 77.2090

    fig = go.Figure()

    # =========================
    # ATTACK POINTS
    # =========================

    fig.add_trace(go.Scattergeo(

        lon=map_df["lon"],
        lat=map_df["lat"],

        text=map_df["ip"] + " | " + map_df["severity"],

        mode="markers",

        marker=dict(
            size=map_df["count"].clip(1, 20) + 5,
            color=map_df["color"],
            opacity=0.8
        ),

        name="Attack Sources"

    ))

    # =========================
    # ATTACK LINES
    # =========================

    for _, row in map_df.iterrows():

        fig.add_trace(go.Scattergeo(

            lon=[row["lon"], target_lon],
            lat=[row["lat"], target_lat],

            mode="lines",

            line=dict(width=1, color="orange"),

            opacity=0.4,

            showlegend=False
        ))

    # =========================
    # PROTECTED SYSTEM
    # =========================

    fig.add_trace(go.Scattergeo(

        lon=[target_lon],
        lat=[target_lat],

        mode="markers",

        marker=dict(size=14, color="cyan"),

        name="Protected System"

    ))

    # =========================
    # STYLE
    # =========================

    fig.update_layout(

        geo=dict(
            showland=True,
            landcolor="rgb(25,25,25)",
            bgcolor="black",
            showocean=True,
            oceancolor="rgb(10,10,10)"
        ),

        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0)

    )

    return fig