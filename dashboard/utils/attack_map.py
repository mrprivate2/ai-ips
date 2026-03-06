import pandas as pd
import plotly.express as px

def build_attack_map(df):

    if df.empty:
        return None

    # Fake geo mapping (for visualization)
    df["lat"] = 20
    df["lon"] = 0

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="source_ip",
        color="attack_type",
        template="plotly_dark"
    )

    fig.update_layout(
        title="Global Attack Visualization"
    )

    return fig