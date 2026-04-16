import pandas as pd
import plotly.express as px


def packet_rate_graph(df):

    # ============================
    # VALIDATION
    # ============================

    if df.empty or "timestamp" not in df.columns:
        return None

    df = df.copy()

    # ============================
    # TIMESTAMP PROCESSING
    # ============================

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    if df.empty:
        return None

    # ============================
    # PACKET RATE
    # ============================

    rate = (
        df.groupby(pd.Grouper(key="timestamp", freq="5s"))
        .size()
        .reset_index(name="events")
    )

    if rate.empty:
        return None

    # ============================
    # SPIKE DETECTION (🔥 IMPORTANT)
    # ============================

    threshold = rate["events"].mean() + 2 * rate["events"].std()
    rate["spike"] = rate["events"] > threshold

    # ============================
    # GRAPH
    # ============================

    fig = px.line(
        rate,
        x="timestamp",
        y="events",
        template="plotly_dark",
        title="Packet Rate (Events / 5s)"
    )

    # highlight spikes
    spikes = rate[rate["spike"]]

    if not spikes.empty:
        fig.add_scatter(
            x=spikes["timestamp"],
            y=spikes["events"],
            mode="markers",
            marker=dict(size=8, color="red"),
            name="Traffic Spike"
        )

    return fig