import pandas as pd
import plotly.express as px
import streamlit as st


class DataPlot:

    @staticmethod
    def create_xray_event_table(event_data):
        if not event_data:
            st.warning("Brak danych o rozbłysku X-Ray.")
            return None

        (satellite, current_class, current_ratio, current_int_xrlong,
         begin_time, begin_class, max_time, max_class,
         max_xrlong, end_time, end_class) = event_data

        def parse_time(time_str):
            if not time_str or time_str == "Unk":
                return "N/A"
            dt = pd.to_datetime(time_str, errors="coerce")
            if pd.isna(dt):
                return "N/A"
            return dt.strftime("%d %b %Y %H:%M:%S GMT")

        current_str = parse_time(begin_time)
        begin_str = parse_time(begin_time)
        max_str = parse_time(max_time)
        end_str = parse_time(end_time)

        try:
            ratio_str = f"Ratio {float(current_ratio):.3f}"
        except (ValueError, TypeError):
            ratio_str = "Ratio N/A"

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

        df['time_tag'] = pd.to_datetime(df['time_tag'])

        df.sort_values("time_tag", ascending=False, inplace=True)

        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)

        df.rename(columns={
            "time_tag": "Znacznik czasu",
            "proton_speed": "Prędkość protonów [km/s]",
            "proton_density": "Gęstość protonów [cm³]",
            "proton_temperature": "Temperatura protonów [K]"
        }, inplace=True)

        return df

    @staticmethod
    def create_solarwind_speed_line_plot(df):
        df_plot = df.copy()

        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None

        min_dt = df_plot["time_tag"].min()
        max_dt = df_plot["time_tag"].max()

        if pd.isna(min_dt) or pd.isna(max_dt):
            st.warning("Brak poprawnego zakresu czasu.")
            return None

        if isinstance(min_dt, pd.Timestamp):
            min_dt = min_dt.to_pydatetime()
        if isinstance(max_dt, pd.Timestamp):
            max_dt = max_dt.to_pydatetime()

        start_dt = st.slider(
            "Wybierz datę/godzinę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_speed_dt_slider"
        )

        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_speed_dt_slider"
        )

        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Nie ma danych w wybranym przedziale czasowym.")
            return None

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
        df_plot = df.copy()

        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None

        min_dt = df_plot["time_tag"].min()
        max_dt = df_plot["time_tag"].max()

        if pd.isna(min_dt) or pd.isna(max_dt):
            st.warning("Brak poprawnego zakresu czasu.")
            return None

        if isinstance(min_dt, pd.Timestamp):
            min_dt = min_dt.to_pydatetime()
        if isinstance(max_dt, pd.Timestamp):
            max_dt = max_dt.to_pydatetime()

        start_dt = st.slider(
            "Wybierz datę/godzinę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_density_dt_slider"
        )

        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_density_dt_slider"
        )

        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Nie ma danych w wybranym przedziale czasowym.")
            return None

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
        df_plot = df.copy()

        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None

        min_dt = df_plot["time_tag"].min()
        max_dt = df_plot["time_tag"].max()

        if pd.isna(min_dt) or pd.isna(max_dt):
            st.warning("Brak poprawnego zakresu czasu.")
            return None

        if isinstance(min_dt, pd.Timestamp):
            min_dt = min_dt.to_pydatetime()
        if isinstance(max_dt, pd.Timestamp):
            max_dt = max_dt.to_pydatetime()

        start_dt = st.slider(
            "Wybierz datę/godzinę początkową:",
            min_value=min_dt,
            max_value=max_dt,
            value=min_dt,
            format="DD-MM-YYYY HH:mm",
            key="start_temp_dt_slider"
        )

        end_dt = st.slider(
            "Wybierz datę/godzinę końcową:",
            min_value=min_dt,
            max_value=max_dt,
            value=max_dt,
            format="DD-MM-YYYY HH:mm",
            key="end_temp_dt_slider"
        )

        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Nie ma danych w wybranym przedziale czasowym.")
            return None

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
        required_columns = {"time_tag", "satellite", "flux"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            st.error(f"Brakuje kolumn w danych: {missing_columns}")
            return None

        df_plot = df.copy()

        df_plot["time_tag"] = pd.to_datetime(df_plot["time_tag"], errors="coerce")

        if df_plot.empty or df_plot["time_tag"].isna().all():
            st.warning("Brak poprawnych danych w 'time_tag' do wyświetlenia wykresu.")
            return None

        min_dt = df_plot["time_tag"].min().to_pydatetime()
        max_dt = df_plot["time_tag"].max().to_pydatetime()

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

        if end_dt < start_dt:
            st.warning("Data końcowa jest wcześniejsza niż data początkowa!")
            return None

        mask = (df_plot["time_tag"] >= start_dt) & (df_plot["time_tag"] <= end_dt)
        df_filtered = df_plot[mask]

        if df_filtered.empty:
            st.warning("Brak danych w wybranym przedziale czasowym.")
            return None

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
        required_columns = {"time_tag", "satellite", "flux"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            st.error(f"Brakuje kolumn w danych: {missing_columns}")
            return None

        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce")

        df_sorted = df.sort_values(by="time_tag", ascending=False).head(20)

        df_sorted = df_sorted.sort_values(by="time_tag")

        fig = px.line(
            df_sorted,
            x="time_tag",
            y="flux",
            color="satellite",
            markers=True,
            labels={
                "time_tag": "Czas",
                "flux": "Natężenie promieniowania (W/m²)",
                "satellite": "Satelita"
            },
            title="Natężenie promieniowania X-ray GOES-16 i GOES-18"
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