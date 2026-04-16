import pandas as pd
import plotly.graph_objects as go


def packet_rate_graph(df):

    # ==============================
    # VALIDATION
    # ==============================

    if df.empty or "timestamp" not in df.columns:
        return None

    df = df.copy()

    # ==============================
    # TIMESTAMP PROCESSING
    # ==============================

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    if df.empty:
        return None

    # ==============================
    # EVENTS PER TIME WINDOW
    # ==============================

    rate = (
        df.groupby(pd.Grouper(key="timestamp", freq="10s"))
        .size()
        .reset_index(name="events")
    )

    if rate.empty:
        return None

    # ==============================
    # SMOOTHING (🔥 IMPORTANT)
    # ==============================

    rate["rolling_avg"] = rate["events"].rolling(window=3, min_periods=1).mean()

    # ==============================
    # SPIKE DETECTION (IMPROVED)
    # ==============================

    mean_rate = rate["events"].mean()
    std_rate = rate["events"].std()

    # fallback for very small datasets
    if pd.isna(std_rate) or std_rate == 0:
        threshold = mean_rate * 2 if mean_rate > 0 else 5
    else:
        threshold = mean_rate + 2 * std_rate

    rate["spike"] = rate["events"] > threshold

    # ==============================
    # BUILD GRAPH
    # ==============================

    fig = go.Figure()

    # Raw traffic
    fig.add_trace(go.Scatter(
        x=rate["timestamp"],
        y=rate["events"],
        mode="lines",
        name="Traffic Rate",
        line=dict(color="cyan", width=2)
    ))

    # Smoothed baseline
    fig.add_trace(go.Scatter(
        x=rate["timestamp"],
        y=rate["rolling_avg"],
        mode="lines",
        name="Baseline",
        line=dict(color="yellow", dash="dash")
    ))

    # Spikes
    spikes = rate[rate["spike"]]

    if not spikes.empty:
        fig.add_trace(go.Scatter(
            x=spikes["timestamp"],
            y=spikes["events"],
            mode="markers",
            name="Traffic Spike",
            marker=dict(color="red", size=8)
        ))

    # ==============================
    # STYLE
    # ==============================

    fig.update_layout(
        template="plotly_dark",
        title="Network Events Per 10 Seconds",
        xaxis_title="Time",
        yaxis_title="Events",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )

    return fig