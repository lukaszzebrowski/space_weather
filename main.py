import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Nasze moduły
from app.db_manager import DBManager
from app.data_fetcher import NOAADataFetcher, XRayDataFetcher
from app.plot import DataPlot
from app.gauge import GaugePlot

st.set_page_config(layout="wide", page_title="Dashboard Pogody Kosmicznej")

class SpaceWeatherDashboard:
    def __init__(self):
        # Baza
        self.db = DBManager()

        # 1) Fetcher wiatru słonecznego (DSCOVR)
        self.wind_url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
        self.wind_fetcher = NOAADataFetcher(self.wind_url)

        # 2) Fetcher X-Ray (latest)
        self.xray_latest_url = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"
        self.xray_fetcher = XRayDataFetcher(self.xray_latest_url)

        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fetch_and_save_solarwind(self):
        """Pobiera dane wiatru, zapisuje najnowszy rekord do bazy, jeśli jest nowy."""
        data = self.wind_fetcher.fetch_data()
        if not data:
            return None

        latest = data[-1]  # ostatni pomiar
        time_tag = latest.get("time_tag", None)
        if not time_tag:
            return None

        # Sprawdzamy w bazie
        if not self.db.check_solarwind_exists(time_tag):
            proton_speed = latest.get("proton_speed", 0.0)
            proton_density = latest.get("proton_density", 0.0)
            self.db.insert_solarwind(time_tag, proton_speed, proton_density)
        return time_tag

    def fetch_and_save_xray(self):
        """Pobiera dane X-Ray (zwykle 1 element) i zapisuje do bazy, jeśli time_tag nowy."""
        data = self.xray_fetcher.fetch_data()
        if not data:
            return None

        # Zakładamy, że data to lista wpisów; bierzemy ostatni
        latest = data[-1]
        time_tag = latest.get("time_tag", None)
        if not time_tag:
            return None

        if not self.db.check_xray_exists(time_tag):
            satellite = latest.get("satellite", None)
            current_class = latest.get("current_class", None)
            current_ratio = latest.get("current_ratio", None)
            current_int_xrlong = latest.get("current_int_xrlong", None)
            begin_time = latest.get("begin_time", None)

            self.db.insert_xray(
                time_tag,
                satellite,
                current_class,
                current_ratio,
                current_int_xrlong,
                begin_time
            )
        return time_tag

    def render_dashboard(self):
        st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {self.last_refresh}</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 2])

        with col1:
            st.subheader("Ostatnie dane X-Ray (z bazy)")
            # Pobierz np. ostatnie 5 wpisów
            xray_rows = self.db.get_recent_xray(limit=4)
            if xray_rows:
                xray_df = DataPlot.create_xray_table(xray_rows)
                st.table(xray_df)
            else:
                st.warning("Brak danych X-Ray w bazie.")

            st.subheader("Wiatr Słoneczny (DSCOVR)")
            # Najnowszy wpis z bazy dla wiatru
            latest_sw = self.db.get_latest_solarwind()
            if latest_sw:
                # (id, time_tag, proton_speed, proton_density)
                _, time_tag_db, speed_db, density_db = latest_sw

                gauge_fig = GaugePlot.create_gauge(speed_db, density_db, time_tag_db)
                st.plotly_chart(gauge_fig, use_container_width=True)

                # (Opcjonalnie) Tabela z 4 wpisami wiatru
                st.write("Ostatnie 4 wpisy wiatru słonecznego:")
                sw_rows = self.db.get_recent_solarwind(limit=4)  # lista krotek z bazy
                df_sw = DataPlot.create_solarwind_table(sw_rows)  # tworzymy DataFrame
                st.table(df_sw)
            else:
                st.warning("Brak danych wiatru słonecznego w bazie.")

        with col2:
            st.subheader("Obrazy Słońca (SOHO)")
            st.image(
                "https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg",
                caption="SOHO LASCO C2",
                use_container_width=True
            )
            st.image(
                "https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg",
                caption="SOHO LASCO C3",
                use_container_width=True
            )
            # Dodaj obraz SDO/HMI
            st.image(
                "https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg",
                caption="SDO/HMI Continuum Image",
                use_container_width=True
            )

    def run(self):
        # Odśwież co minutę
        st_autorefresh(interval=60000, limit=None, key="data_refresh")
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1) Pobierz i zapisz dane DSCOVR
        self.fetch_and_save_solarwind()

        # 2) Pobierz i zapisz dane X-Ray
        self.fetch_and_save_xray()

        # 3) Renderuj
        self.render_dashboard()


if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
