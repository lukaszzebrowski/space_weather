import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class DataPlot:
    @staticmethod
    def create_7_day_xray_plot(data):
        """Tworzy wykres promieniowania rentgenowskiego z 7 dni."""
        df = pd.DataFrame(data)
        # Konwersja kolumn na datetime
        df['time_tag'] = pd.to_datetime(df['time_tag'])

        fig = go.Figure()

        # Wartości XR-long (natężenie)
        fig.add_trace(go.Scatter(
            x=df['time_tag'],
            y=df['current_int_xrlong'],
            mode='lines',
            name='XR-long (natężenie promieniowania)',
            line=dict(color='orange')
        ))

        # Ustawienia wykresu
        fig.update_layout(
            title="Promieniowanie rentgenowskie (7 dni)",
            xaxis_title="Czas (UTC)",
            yaxis_title="Natężenie XR-long (Watty · m⁻²)",
            yaxis_type="log",  # Skala logarytmiczna
            legend_title="Typ promieniowania",
            width=1000,
            height=600
        )

        return fig

    @staticmethod
    def create_line_chart(data):
        """Tworzy wykres liniowy z danych promieniowania rentgenowskiego."""
        df = pd.DataFrame(data)
        # Konwersja czasu na datetime dla lepszej wizualizacji
        df['time_tag'] = pd.to_datetime(df['time_tag'])

        fig = px.line(
            df,
            x='time_tag',
            y='current_int_xrlong',
            title="Natężenie promieniowania rentgenowskiego w czasie",
            labels={'time_tag': 'Czas', 'current_int_xrlong': 'Natężenie XR-long'},
            markers=True
        )
        fig.update_layout(width=900, height=500)
        return fig

    @staticmethod
    def create_table(data):
        """Tworzy tabelę z aktualnymi danymi promieniowania."""
        df = pd.DataFrame(data)
        # Wybieramy interesujące nas kolumny i zmieniamy ich nazwy dla czytelności
        df = df[[
            "time_tag",
            "satellite",
            "current_class",
            "current_int_xrlong",
            "begin_time",
            "max_time",
            "end_time",
            "max_class"
        ]]
        df.rename(columns={
            "time_tag": "Czas pomiaru",
            "satellite": "Satelita",
            "current_class": "Aktualna klasa",
            "current_int_xrlong": "Natężenie XR-long",
            "begin_time": "Czas rozpoczęcia",
            "max_time": "Czas maksymalny",
            "end_time": "Czas zakończenia",
            "max_class": "Maks. klasa"
        }, inplace=True)

        return df
