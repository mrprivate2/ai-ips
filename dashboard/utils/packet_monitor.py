import pandas as pd
import plotly.express as px

def packet_rate_graph(df):

    if df.empty:
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    rate = (
        df.groupby(pd.Grouper(key="timestamp", freq="5s"))
        .size()
        .reset_index(name="events")
    )

    fig = px.line(
        rate,
        x="timestamp",
        y="events",
        template="plotly_dark",
        title="Packet Rate (Events / 5s)"
    )

    return fig