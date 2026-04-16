import pandas as pd
import plotly.express as px
import requests

# =============================
# GEO CACHE
# =============================

geo_cache = {}

def get_ip_location(ip):

    if ip in geo_cache:
        return geo_cache[ip]

    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=lat,lon,country",
            timeout=2
        )
        data = r.json()

        if data.get("lat"):
            geo_cache[ip] = (data["lat"], data["lon"], data["country"])
            return geo_cache[ip]

    except:
        pass

    geo_cache[ip] = (None, None, "Unknown")
    return geo_cache[ip]


# =============================
# BUILD MAP
# =============================

def build_attack_map(df):

    if df.empty or "source_ip" not in df.columns:
        return None

    attackers = []

    # 🔥 optimized grouping
    grouped = df.groupby("source_ip")

    for ip, group in grouped:

        lat, lon, country = get_ip_location(ip)

        if lat is None:
            continue

        count = len(group)

        # 🔥 anomaly detection
        has_anomaly = False
        if "attack_type" in group.columns:
            has_anomaly = any(group["attack_type"] == "UNKNOWN_THREAT")

        # 🔥 severity logic
        if has_anomaly:
            severity = "HIGH"
        elif count > 20:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        attackers.append({
            "ip": ip,
            "lat": lat,
            "lon": lon,
            "country": country,
            "count": count,
            "severity": severity
        })

    map_df = pd.DataFrame(attackers)

    if map_df.empty:
        return None

    # =============================
    # VISUALIZATION
    # =============================

    fig = px.scatter_geo(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="ip",
        size="count",
        color="severity",
        template="plotly_dark",
        projection="natural earth",
        color_discrete_map={
            "HIGH": "red",
            "MEDIUM": "orange",
            "LOW": "green"
        }
    )

    fig.update_layout(
        title="🌍 Global Attack Intelligence Map",
        legend_title="Threat Severity"
    )

    return fig