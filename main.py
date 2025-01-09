import streamlit as st
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Z plików:
from app.api import NOAADataFetcher, XRayDataFetcher  # Zakładamy, że tam jest klasa XRayDataFetcher
from app.plot import DataPlot  # zawiera create_table
from app.gauge import GaugePlot
from app.utils import DataProcessor  # ma process_xray_latest_data, get_latest_xray_measure

st.set_page_config(layout="wide", page_title="Dashboard Pogody Kosmicznej")

class SpaceWeatherDashboard:
    def __init__(self):
        # 1) Wiatr słoneczny (DSCOVR)
        self.wind_url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
        self.fetcher = NOAADataFetcher(self.wind_url)  # klasa NOAADataFetcher powinna istnieć w app/api.py

        # 2) Dane X-Ray (ostatnie)
        self.xray_latest_url = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"
        self.xray_fetcher = XRayDataFetcher(self.xray_latest_url)

        self.processor = DataProcessor()
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fetch_and_process_data(self):
        """
        Pobiera i przetwarza dane z NOAA (wiatr słoneczny) i XRay (latest).
        """
        # 1) Wiatr słoneczny
        wind_raw = self.fetcher.fetch_data()
        dscovr_data = self.processor.filter_dscovr_data(wind_raw)
        latest_wind = self.processor.get_latest_data(dscovr_data)  # np. get_latest_data

        # 2) XRay bieżące
        xray_raw = self.xray_fetcher.fetch_data()
        xray_data = self.processor.process_xray_latest_data(xray_raw)
        # to jest lista wpisów, w xray-flares-latest może być 1 lub kilka
        # do tabeli użyjemy wszystkich, do "najnowszego wpisu" ewentualnie get_latest_xray_measure
        #latest_xray_measure = self.processor.get_latest_xray_measure(xray_data)

        return latest_wind, xray_data

    def render_dashboard(self, latest_wind, xray_data):
        st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {self.last_refresh}</h4>",
                    unsafe_allow_html=True)

        # Dwie kolumny
        col1, col2 = st.columns([2,2])

        with col1:
            # 1) Tabela X-Ray
            st.subheader("Ostatnie dane X-Ray (GOES)")
            if xray_data:
                # create_table zwraca DataFrame
                xray_df = DataPlot.create_table(xray_data)
                st.table(xray_df)
            else:
                st.warning("Brak danych z X-Ray (latest).")

            # 2) Wskaźnik prędkości wiatru słonecznego
            st.subheader("Wiatr Słoneczny (DSCOVR)")
            if latest_wind:
                proton_speed = latest_wind.get("proton_speed", 0)
                density = latest_wind.get("proton_density", 0)
                time_tag = latest_wind.get("time_tag", "Brak danych")
                gauge_fig = GaugePlot.create_gauge(proton_speed, density, time_tag)
                st.plotly_chart(gauge_fig, use_container_width=True)
            else:
                st.warning("Brak danych z DSCOVR.")
            st.image(
                "https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg",
                caption="SDO/HMI Continuum Image",
                use_container_width=True
            )
        with col2:
            st.subheader("Obrazy Słońca")
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

    def run(self):
        st_autorefresh(interval=60000, limit=None, key="data_refresh")
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        latest_wind, xray_data = self.fetch_and_process_data()
        self.render_dashboard(latest_wind, xray_data)

if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
