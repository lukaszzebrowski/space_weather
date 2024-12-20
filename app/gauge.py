import plotly.graph_objects as go

class GaugePlot:
    @staticmethod
    def create_gauge(speed, density, time_tag):
        """Tworzy wykres gauge z podanymi danymi."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=speed,
            title={'text': f"Prędkość protonów: <b>{speed}(km/s)</b><br>"
                           f"Gęstość protonów: <b>{density} protons/cm3</b><br>"
                           f"Ostatni pomiar: <b>{time_tag}</b>",
                   'font': {'size': 30}},
            gauge={
                'axis': {'range': [0, 1000], 'tickwidth': 1, 'tickcolor': "darkblue", 'dtick': 50},
                'bar': {'color': "orange"},
                'steps': [
                    {'range': [0, 300], 'color': "green"},
                    {'range': [300, 600], 'color': "yellow"},
                    {'range': [600, 1000], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': speed
                }
            }
        ))
        fig.update_layout(
            autosize=False,
            width=1000,
            height=700,
            margin=dict(l=80, r=80, t=50, b=50)
        )
        return fig
