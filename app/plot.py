import pandas as pd
import plotly.express as px
import streamlit as st


class DataPlot:

    @staticmethod
    def create_xray_event_table(event_data):
        """
        Tworzy tabelę dla najnowszego rozbłysku X-Ray w formacie:
        Current, Beginning, Maximum, End.
        Oczekujemy, że event_data to krotka o polach:
        (
          satellite, current_class, current_ratio, current_int_xrlong,
          begin_time, begin_class, max_time, max_class,
          max_xrlong, end_time, end_class
        )
        """

        if not event_data:
            st.warning("Brak danych o rozbłysku X-Ray.")
            return None

        (satellite, current_class, current_ratio, current_int_xrlong,
         begin_time, begin_class, max_time, max_class,
         max_xrlong, end_time, end_class) = event_data

        def parse_time(time_str):
            """
            Funkcja pomocnicza do konwersji czasu na format '%d %b %Y %H:%M:%S GMT'.
            Jeśli time_str to 'Unk' lub nie da się sparsować, zwraca 'N/A'.
            """
            if not time_str or time_str == "Unk":
                return "N/A"
            dt = pd.to_datetime(time_str, errors="coerce")
            if pd.isna(dt):
                return "N/A"
            return dt.strftime("%d %b %Y %H:%M:%S GMT")

        # Konwersja pól czasowych:
        # W oryginalnym kodzie 'Current' i 'Beginning' używały begin_time,
        # jeśli chcesz inny czas dla Current, musisz go pobrać z innego pola.
        current_str = parse_time(begin_time)
        begin_str = parse_time(begin_time)
        max_str = parse_time(max_time)
        end_str = parse_time(end_time)

        # Obsługa current_ratio
        try:
            ratio_str = f"Ratio {float(current_ratio):.3f}"
        except (ValueError, TypeError):
            ratio_str = "Ratio N/A"

        # Obsługa max_xrlong
        try:
            flux_str = f"Integrated flux: {float(max_xrlong):.1e} J m-2"
        except (ValueError, TypeError):
            flux_str = "Integrated flux: N/A"

        data = {
            "Faza": ["Current", "Beginning", "Maximum", "End"],
            "Czas": [current_str, begin_str, max_str, end_str],
            "Klasa rozbłysku": [current_class, begin_class, max_class, end_class],
            "Dodatkowe dane": [ratio_str, "", flux_str, ""]
        }

        df = pd.DataFrame(data)
        st.table(df)

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
            "proton_density",
            "proton_temperature"
        ])

        df["proton_temperature"] = df["proton_temperature"].apply(lambda x: f"{x:.2e}")
        df["proton_speed"] = df["proton_speed"].apply(lambda x: f"{x:.2f}")
        df.drop(columns=["ID"], inplace=True)


        # Konwersja na datetime z interpretacją strefy jako UTC
        df['time_tag'] = pd.to_datetime(df['time_tag'])

        # Sortowanie rosnąco
        df.sort_values("time_tag", ascending=False, inplace=True)

        # Formatowanie
        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)  # Ustawiamy puste etykiety dla każdego wiersza

        df.rename(columns={
            "time_tag": "Znacznik czasu",
            "proton_speed": "Prędkość protonów [km/s]",
            "proton_density": "Gęstość protonów [cm³]",
            "proton_temperature": "Temperatura protonów [K]"
        }, inplace=True)

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

    @staticmethod
    def create_solarwind_temp_line_plot(df):
        """
        Tworzy wykres liniowy z danymi wiatru słonecznego (temperatury protonów w czasie).
        Zamiast jednego dwustronnego suwaka, mamy dwa osobne suwaki:
         - 'start_dt' (data początkowa)
         - 'end_dt' (data końcowa).

        df to DataFrame z kolumnami:
         - 'time_tag' (string lub datetime)
         - 'proton_density'
         - 'proton_temperature'
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
            key="start_temp_dt_slider"
        )

        # 6. Suwak dla daty końcowej
        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_temp_dt_slider"
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
            y="proton_temperature",
            title="Temperatura protonów w czasie",
            labels={"time_tag": "Czas", "proton_temperature": "Temperatura (K)"}
        )
        fig.update_layout(width=800, height=500)

        return fig

    @staticmethod
    def create_goes_flux_line_plot(df):
        """
        Tworzy wykres liniowy natężenia promieniowania X-ray (flux) w czasie
        dla satelitów GOES-16 i GOES-18.
        """

        # 1. Sprawdzenie obecności wymaganych kolumn
        required_columns = {"time_tag", "satellite", "flux"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            st.error(f"Brakuje kolumn w danych: {missing_columns}")
            return None

        # 2. Kopia DataFrame, by nie modyfikować oryginału
        df_plot = df.copy()

        # 3. Konwersja 'time_tag' do datetime
        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        # 4. Sprawdzenie, czy dane są poprawne
        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None

        # 5. Ustalenie zakresu dat i konwersja na datetime.datetime
        min_dt = df_plot["time_tag"].min().to_pydatetime()
        max_dt = df_plot["time_tag"].max().to_pydatetime()

        # 6. Suwaki do wyboru zakresu dat
        start_dt = st.slider(
            "Wybierz datę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_flux_dt_slider"
        )

        end_dt = st.slider(
            "Wybierz datę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_flux_dt_slider"
        )

        # 7. Walidacja zakresu dat
        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        # 8. Filtrowanie danych w wybranym przedziale czasowym
        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Brak danych w wybranym przedziale czasowym.")
            return None

        # 9. Wykres - dwie linie dla satelitów 16 i 18
        fig = px.line(
            df_filtered,
            x="time_tag",
            y="flux",
            color="satellite",
            labels={
                "time_tag": "Czas",
                "flux": "Natężenie promieniowania (W/m²)",
                "satellite": "Satelita"
            },
            title="Natężenie promieniowania X-ray GOES-16 i GOES-18 w czasie"
        )

        fig.update_layout(
            width=900,
            height=500,
            legend_title_text="Satelita",
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255,255,255,0)',
                bordercolor='rgba(0,0,0,0)'
            )
        )

        return fig

    @staticmethod
    def create_goes_flux_simple_plot(df):
        """
        Tworzy prosty wykres liniowy natężenia promieniowania X-ray (flux)
        w czasie dla ostatnich 20 wyników z satelitów GOES-16 i GOES-18.
        """

        # 1. Sprawdzenie obecności wymaganych kolumn
        required_columns = {"time_tag", "satellite", "flux"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            st.error(f"Brakuje kolumn w danych: {missing_columns}")
            return None

        # 2. Konwersja 'time_tag' do datetime
        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce")

        # 3. Sortowanie danych malejąco po czasie i pobranie ostatnich 20 wyników
        df_sorted = df.sort_values(by="time_tag", ascending=False).head(20)

        # 4. Sortowanie rosnąco dla poprawnego wykresu
        df_sorted = df_sorted.sort_values(by="time_tag")

        # 5. Tworzenie wykresu
        fig = px.line(
            df_sorted,
            x="time_tag",
            y="flux",
            color="satellite",
            markers=True,  # Dodaje punkty danych na linii
            labels={
                "time_tag": "Czas",
                "flux": "Natężenie promieniowania (W/m²)",
                "satellite": "Satelita"
            },
            title="Natężenie promieniowania X-ray GOES-16 i GOES-18 (20 ostatnich wyników)"
        )

        fig.update_layout(
            width=900,
            height=500,
            legend_title_text="Satelita",
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255,255,255,0)',
                bordercolor='rgba(0,0,0,0)'
            )
        )

        return fig