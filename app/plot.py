import pandas as pd
import plotly.express as px
import streamlit as st


class DataPlot:
    @staticmethod
    def create_xray_table(data):
        """
        Tworzy DataFrame z danymi X-Ray i zwraca go,
        posortowany według time_tag (od najstarszego do najnowszego),
        a następnie formatuje kolumnę time_tag jako "YYYY-MM-DD HH:MM:SS" bez strefy czasowej.

        data to lista krotek: (id, time_tag, satellite, current_class,
                               current_ratio, current_int_xrlong, begin_time)
        """
        df = pd.DataFrame(data, columns=[
            "ID",
            "time_tag",
            "satellite",
            "current_class",
            "current_ratio",
            "current_int_xrlong",
            "begin_time"
        ])

        # Usuwamy kolumnę ID, jeśli nie chcesz jej wyświetlać
        df.drop(columns=["ID"], inplace=True)

        # 1) Konwersja na datetime (z interpretacją ewentualnej strefy jako UTC)
        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce", utc=True)

        # 2) Usuwamy strefę czasową, staje się „naiwny” czas
        df["time_tag"] = df["time_tag"].dt.tz_localize(None)

        # 3) Sortowanie rosnąco po time_tag (najstarsze na górze)
        df.sort_values("time_tag", ascending=False, inplace=True)

        # 4) Formatowanie do "YYYY-MM-DD HH:MM:SS"
        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)  # Ustawiamy puste etykiety dla każdego wiersza

        return df

    @staticmethod
    def create_solarwind_table(data):
        """
        Tworzy DataFrame z danymi wiatru słonecznego i zwraca go,
        posortowany według time_tag (od najstarszego do najnowszego),
        a następnie formatuje kolumnę time_tag jako "YYYY-MM-DD HH:MM:SS" bez strefy czasowej.

        data to lista krotek: (id, time_tag, proton_speed, proton_density)
        """
        df = pd.DataFrame(data, columns=[
            "ID",
            "time_tag",
            "proton_speed",
            "proton_density"
        ])

        df.drop(columns=["ID"], inplace=True)

        # Konwersja na datetime z interpretacją strefy jako UTC
        df['time_tag'] = pd.to_datetime(df['time_tag'])

        # Sortowanie rosnąco
        df.sort_values("time_tag", ascending=False, inplace=True)

        # Formatowanie
        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)  # Ustawiamy puste etykiety dla każdego wiersza

        return df

    @staticmethod
    def create_solarwind_speed_line_plot(df):
        """
        Tworzy wykres liniowy z danymi wiatru słonecznego (prędkość protonów w czasie).
        Zamiast jednego dwustronnego suwaka, mamy dwa osobne suwaki:
         - 'start_dt' (data początkowa)
         - 'end_dt' (data końcowa).

        df to DataFrame z kolumnami:
         - 'time_tag' (string lub datetime)
         - 'proton_speed'
        """

        # 1. Kopiujemy DF, by nie modyfikować oryginału
        df_plot = df.copy()

        # 2. Konwertujemy 'time_tag' na datetime (jeśli to już datetime, errors="coerce" nie zaszkodzi)
        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        # 3. Sprawdzamy, czy nie mamy pustego DF lub samych NaT w time_tag
        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None  # Nie zwracamy wykresu

        # 4. Wyznaczamy min i max (mogą być pd.Timestamp), więc konwertujemy na natywne datetime
        min_dt = df_plot["time_tag"].min()
        max_dt = df_plot["time_tag"].max()

        if pd.isna(min_dt) or pd.isna(max_dt):
            st.warning("Brak poprawnego zakresu czasu.")
            return None

        # Konwersja do obiektu datetime.datetime (jeśli to pd.Timestamp)
        if isinstance(min_dt, pd.Timestamp):
            min_dt = min_dt.to_pydatetime()
        if isinstance(max_dt, pd.Timestamp):
            max_dt = max_dt.to_pydatetime()

        # 5. Suwak dla daty początkowej
        start_dt = st.slider(
            "Wybierz datę/godzinę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_speed_dt_slider"
        )

        # 6. Suwak dla daty końcowej
        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_speed_dt_slider"
        )

        # Upewniamy się, że end_dt >= start_dt (można np. zabezpieczyć się warunkiem)
        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        # 7. Filtrowanie DF do wybranego zakresu
        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Nie ma danych w wybranym przedziale czasowym.")
            return None

        # 8. Tworzymy wykres liniowy (Plotly Express)
        fig = px.line(
            df_filtered,
            x="time_tag",
            y="proton_speed",
            title="Prędkość protonów w czasie",
            labels={"time_tag": "Czas", "proton_speed": "Prędkość (km/s)"}
        )
        fig.update_layout(width=800, height=500)

        return fig

    @staticmethod
    def create_solarwind_density_line_plot(df):
        """
        Tworzy wykres liniowy z danymi wiatru słonecznego (gęstość protonów w czasie).
        Zamiast jednego dwustronnego suwaka, mamy dwa osobne suwaki:
         - 'start_dt' (data początkowa)
         - 'end_dt' (data końcowa).

        df to DataFrame z kolumnami:
         - 'time_tag' (string lub datetime)
         - 'proton_density'
        """

        # 1. Kopiujemy DF, by nie modyfikować oryginału
        df_plot = df.copy()

        # 2. Konwertujemy 'time_tag' na datetime (jeśli to już datetime, errors="coerce" nie zaszkodzi)
        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        # 3. Sprawdzamy, czy nie mamy pustego DF lub samych NaT w time_tag
        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None  # Nie zwracamy wykresu

        # 4. Wyznaczamy min i max (mogą być pd.Timestamp), więc konwertujemy na natywne datetime
        min_dt = df_plot["time_tag"].min()
        max_dt = df_plot["time_tag"].max()

        if pd.isna(min_dt) or pd.isna(max_dt):
            st.warning("Brak poprawnego zakresu czasu.")
            return None

        # Konwersja do obiektu datetime.datetime (jeśli to pd.Timestamp)
        if isinstance(min_dt, pd.Timestamp):
            min_dt = min_dt.to_pydatetime()
        if isinstance(max_dt, pd.Timestamp):
            max_dt = max_dt.to_pydatetime()

        # 5. Suwak dla daty początkowej
        start_dt = st.slider(
            "Wybierz datę/godzinę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_density_dt_slider"
        )

        # 6. Suwak dla daty końcowej
        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_density_dt_slider"
        )

        # Upewniamy się, że end_dt >= start_dt (można np. zabezpieczyć się warunkiem)
        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        # 7. Filtrowanie DF do wybranego zakresu
        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Nie ma danych w wybranym przedziale czasowym.")
            return None

        # 8. Tworzymy wykres liniowy (Plotly Express)
        fig = px.line(
            df_filtered,
            x="time_tag",
            y="proton_density",
            title="Gęstość protonów w czasie",
            labels={"time_tag": "Czas", "proton_density": "Gęstość (protons/cm3)"}
        )
        fig.update_layout(width=800, height=500)

        return fig