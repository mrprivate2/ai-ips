import plotly.graph_objects as go

def threat_gauge(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "AI Threat Confidence"},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': "red"},
            'steps': [
                {'range': [0, 0.3], 'color': "green"},
                {'range': [0.3, 0.7], 'color': "orange"},
                {'range': [0.7, 1], 'color': "red"}
            ]
        }
    ))

    return fig