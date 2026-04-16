import plotly.graph_objects as go


def threat_gauge(score):

    # ==============================
    # VALIDATION
    # ==============================

    if score is None:
        score = 0

    # clamp between 0 and 1
    score = max(0, min(score, 1))

    # ==============================
    # BUILD GAUGE
    # ==============================

    fig = go.Figure(go.Indicator(

        mode="gauge+number",

        value=score * 100,

        number={'suffix': "%"},

        title={'text': "Threat Level"},

        gauge={

            'axis': {'range': [0, 100]},

            'bar': {'color': "red"},

            'steps': [
                {'range': [0, 30], 'color': "green"},     # normal
                {'range': [30, 70], 'color': "orange"},   # suspicious
                {'range': [70, 100], 'color': "red"}      # high threat
            ]
        }
    ))

    return fig