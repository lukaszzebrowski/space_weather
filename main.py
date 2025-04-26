import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd

from app.db_manager import DBManager
from app.data_fetcher import (NOAADataFetcher, XRayDataFetcher,
                              GOESSecondaryFetcher, GOESPrimaryFetcher, SolarImageFetcher)
from app.plot import DataPlot
from app.gauge import GaugePlot

st.set_page_config(
    layout="wide",
    page_title="Dashboard Pogody Kosmicznej",
    page_icon="☀️",
    initial_sidebar_state="collapsed"
)

class SpaceWeatherDashboard:
    def __init__(self):
        self.db = DBManager()

        self.wind_fetcher = NOAADataFetcher()

        self.xray_fetcher = XRayDataFetcher()

        self.goes_primary_fetcher = GOESPrimaryFetcher()

        self.goes_secondary_fetcher = GOESSecondaryFetcher()

        self.image_fetcher = SolarImageFetcher()

        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fetch_and_save_solarwind(self):
        data = self.wind_fetcher.fetch_data()
        if not data:
            return None

        latest = data[0]
        time_tag = latest.get("time_tag", None)
        if not time_tag:
            return None

        if not self.db.check_solarwind_exists(time_tag):
            proton_speed = latest.get("proton_speed", 0.0)
            proton_density = latest.get("proton_density", 0.0)
            proton_temperature = latest.get("proton_temperature", 0.0)
            self.db.insert_solarwind(time_tag, proton_speed, proton_density, proton_temperature)
        return time_tag

    def fetch_and_save_xray(self):
        data = self.xray_fetcher.fetch_data()
        if not data:
            return None

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
            begin_class = latest.get("begin_class", None)
            max_time = latest.get("max_time", None)
            max_class = latest.get("max_class", None)
            max_xrlong = latest.get("max_xrlong", None)
            end_time = latest.get("end_time", None)
            end_class = latest.get("end_class", None)

            self.db.insert_xray(
                time_tag,
                satellite,
                current_class,
                current_ratio,
                current_int_xrlong,
                begin_time,
                begin_class,
                max_time,
                max_class,
                max_xrlong,
                end_time,
                end_class
            )
        return time_tag
    def fetch_and_save_goes(self):
        primary_data = self.goes_primary_fetcher.fetch_data()
        if primary_data:
            self._save_goes_data(primary_data)

        secondary_data = self.goes_secondary_fetcher.fetch_data()
        if secondary_data:
            self._save_goes_data(secondary_data)

    def _save_goes_data(self, data):
        for record in data:
            time_tag = record.get("time_tag")
            satellite = record.get("satellite")
            flux = record.get("flux")
            observed_flux = record.get("observed_flux")
            electron_correction = record.get("electron_correction")
            electron_contamination = record.get("electron_contaminaton")
            energy = record.get("energy")

            if not time_tag or satellite is None:
                continue

            if not self.db.check_goes_data_exists(time_tag, satellite):
                self.db.insert_goes_data(
                    time_tag,
                    satellite,
                    flux,
                    observed_flux,
                    electron_correction,
                    electron_contamination,
                    energy
                )

    def fetch_and_save_solar_images(self):
        images = self.image_fetcher.fetch_images()
        for img in images:
            if not self.db.check_image_exists(img["source"], img["image_hash"]):
                self.db.insert_solar_image(
                    img["source"],
                    img["image_data"],
                    img["image_hash"],
                    img["time_tag"]
                )
                print(f"Zapisano nowy obraz: {img['source']}")
            else:
                print(f"Obraz z {img['source']} już istnieje. Pomijam zapis.")

    def render_dashboard(self):
        st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {self.last_refresh}</h4>", unsafe_allow_html=True)

        col1, col2 = st.columns([2, 2])

        with col1:
            st.subheader("Wiatr Słoneczny (DSCOVR)")
            sw_rows = self.db.get_recent_solarwind(limit=4)
            df_sw = DataPlot.create_solarwind_table(sw_rows)
            st.table(df_sw)
            latest_sw = self.db.get_latest_solarwind()
            if latest_sw:
                _, time_tag_db, speed_db, density_db, *rest = latest_sw

                gauge_fig = GaugePlot.create_gauge(speed_db, density_db, time_tag_db)
                st.plotly_chart(gauge_fig, use_container_width=True)
            else:
                st.warning("Brak danych wiatru słonecznego w bazie.")
            st.subheader("Natężenie promieniowania X-Ray (GOES)")

            goes_rows = self.db.get_recent_goes_data(limit=20)

            if goes_rows:
                df_goes = pd.DataFrame(goes_rows, columns=[
                    "id",
                    "time_tag",
                    "satellite",
                    "flux",
                    "observed_flux",
                    "electron_correction",
                    "electron_contamination",
                    "energy"
                ])

                df_goes.drop(columns=["id"], inplace=True, errors='ignore')

                fig_goes_flux = DataPlot.create_goes_flux_simple_plot(df_goes)

                if fig_goes_flux:
                    st.plotly_chart(fig_goes_flux, use_container_width=True)
                else:
                    st.warning("Brak danych do wyświetlenia wykresu.")
            else:
                st.warning("Brak danych GOES w bazie.")

            st.subheader("Dane X-Ray")
            st.subheader("GOES-16 Najnowszy rozbłysk X-Ray")

            latest_xray_event = self.db.get_latest_xray_event()
            if latest_xray_event:
                DataPlot.create_xray_event_table(latest_xray_event)
            else:
                st.warning("Brak danych o najnowszym rozbłysku X-Ray.")

        with col2:
            st.subheader("Obrazy Słońca (SOHO/SDO)")

            images = self.db.get_latest_solar_images()

            if images:
                for source, image_data, time_tag in images:
                    st.image(image_data, caption=f"{source} (pobrano: {time_tag})",use_container_width=True)
            else:
                st.warning("Brak zapisanych obrazów w bazie.")

    def run(self):

        st_autorefresh(interval=60000, limit=None, key="data_refresh")
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.fetch_and_save_solarwind()

        self.fetch_and_save_xray()

        self.fetch_and_save_goes()

        self.fetch_and_save_solar_images()

        self.render_dashboard()


if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
