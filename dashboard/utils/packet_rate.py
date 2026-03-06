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
    # TRAFFIC SPIKE DETECTION
    # ==============================

    mean_rate = rate["events"].mean()

    spike_threshold = mean_rate * 2 if mean_rate > 0 else 10

    rate["spike"] = rate["events"] > spike_threshold

    # ==============================
    # BUILD GRAPH
    # ==============================

    fig = go.Figure()

    # Normal traffic line
    fig.add_trace(go.Scatter(

        x=rate["timestamp"],
        y=rate["events"],

        mode="lines",

        name="Traffic Rate",

        line=dict(
            color="cyan",
            width=2
        )
    ))

    # Traffic spikes
    spike_points = rate[rate["spike"]]

    if not spike_points.empty:

        fig.add_trace(go.Scatter(

            x=spike_points["timestamp"],
            y=spike_points["events"],

            mode="markers",

            name="Traffic Spike",

            marker=dict(
                color="red",
                size=8
            )
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