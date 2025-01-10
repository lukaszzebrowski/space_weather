import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# Nasze moduły
from app.db_manager import DBManager
from app.data_fetcher import (NOAADataFetcher, XRayDataFetcher, APODDataFetcher,
                              GOESSecondaryFetcher, GOESPrimaryFetcher, SolarImageFetcher)
from app.plot import DataPlot
from app.gauge import GaugePlot

# Ustawienia strony Streamlit
st.set_page_config(
    layout="wide",
    page_title="Dashboard Pogody Kosmicznej",
    page_icon="☀️",
    initial_sidebar_state="collapsed"  # Opcje: "auto", "expanded", "collapsed"
)
def set_background_image(image_url):
    """
    Ustawia tło aplikacji Streamlit za pomocą CSS.
    """
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
class SpaceWeatherDashboard:
    def __init__(self):
        # Baza
        self.db = DBManager()

        # 1) Fetcher wiatru słonecznego (DSCOVR)
        self.wind_fetcher = NOAADataFetcher()

        # 2) Fetcher X-Ray (latest)
        self.xray_fetcher = XRayDataFetcher()

        # Fetcher dla NASA APOD
        self.apod_fetcher = APODDataFetcher()  # Dodanie fetchera dla NASA APOD

        # Inicjalizacja fetchera dla GOES Primary
        self.goes_primary_fetcher = GOESPrimaryFetcher()

        # Inicjalizacja fetchera dla GOES Secondary
        self.goes_secondary_fetcher = GOESSecondaryFetcher()

        # Inicjalizacja pobierania obrazów
        self.image_fetcher = SolarImageFetcher()

        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def set_dashboard_background(self):
        """
        Pobiera i ustawia tło z NASA APOD.
        """
        image_url = self.apod_fetcher.fetch_background_image_url()
        if image_url:
            set_background_image(image_url)
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
            proton_temperature = latest.get("proton_temperature", 0.0)  # dodanie temperatury do bazy
            self.db.insert_solarwind(time_tag, proton_speed, proton_density, proton_temperature)
        return time_tag

    def fetch_and_save_xray(self):
        """Pobiera dane X-Ray i zapisuje do bazy, jeśli time_tag jest nowy."""
        data = self.xray_fetcher.fetch_data()
        if not data:
            return None

        # Pobieramy najnowszy pomiar
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

            # Dodajemy nowe dane do zapisu
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
        """Pobiera dane GOES (Primary i Secondary) i zapisuje do bazy, jeśli rekord jest nowy."""

        # Pobierz dane z GOES Primary
        primary_data = self.goes_primary_fetcher.fetch_data()
        if primary_data:
            self._save_goes_data(primary_data)

        # Pobierz dane z GOES Secondary
        secondary_data = self.goes_secondary_fetcher.fetch_data()
        if secondary_data:
            self._save_goes_data(secondary_data)

    def _save_goes_data(self, data):
        """Pomocnicza metoda do zapisu danych GOES do bazy."""

        for record in data:
            time_tag = record.get("time_tag")
            satellite = record.get("satellite")
            flux = record.get("flux")
            observed_flux = record.get("observed_flux")
            electron_correction = record.get("electron_correction")
            electron_contamination = record.get("electron_contaminaton")  # Uwaga: literówka w API
            energy = record.get("energy")

            # Sprawdzamy, czy time_tag i satellite są obecne
            if not time_tag or satellite is None:
                continue  # Pomijamy niekompletne rekordy

            # Sprawdzamy, czy rekord już istnieje w bazie
            if not self.db.check_goes_data_exists(time_tag, satellite):
                # Zapis do bazy
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
        """Pobiera i zapisuje obrazy SOHO/SDO do bazy danych."""
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
            # Tabela z 4 wpisami wiatru
            sw_rows = self.db.get_recent_solarwind(limit=4)  # lista krotek z bazy
            df_sw = DataPlot.create_solarwind_table(sw_rows)  # tworzymy DataFrame
            st.table(df_sw)
            # Najnowszy wpis z bazy dla wiatru
            latest_sw = self.db.get_latest_solarwind()
            if latest_sw:
                # (id, time_tag, proton_speed, proton_density)
                _, time_tag_db, speed_db, density_db, *rest = latest_sw

                gauge_fig = GaugePlot.create_gauge(speed_db, density_db, time_tag_db)
                st.plotly_chart(gauge_fig, use_container_width=True)
            else:
                st.warning("Brak danych wiatru słonecznego w bazie.")
            st.subheader("Natężenie promieniowania X-Ray (GOES)")

            # 1. Pobranie danych GOES
            goes_rows = self.db.get_recent_goes_data(limit=20)  # Pobranie 20 najnowszych wyników

            # 2. Sprawdzenie, czy są dane
            if goes_rows:
                # 3. Tworzenie DataFrame
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

                # 4. Usunięcie kolumny ID (jeśli niepotrzebna)
                df_goes.drop(columns=["id"], inplace=True, errors='ignore')

                # 5. Wykres dla 20 ostatnich wyników
                fig_goes_flux = DataPlot.create_goes_flux_simple_plot(df_goes)

                if fig_goes_flux:
                    st.plotly_chart(fig_goes_flux, use_container_width=True)
                else:
                    st.warning("Brak danych do wyświetlenia wykresu.")
            else:
                st.warning("Brak danych GOES w bazie.")

            st.subheader("Dane X-Ray")
            # Pobierz np. ostatnie x wpisów
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
        # Ustaw tło
        self.set_dashboard_background()

        # Odśwież co minutę
        st_autorefresh(interval=60000, limit=None, key="data_refresh")
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Pobierz i zapisz dane DSCOVR (wiatr słoneczny)
        self.fetch_and_save_solarwind()

        # Pobierz i zapisz dane X-Ray
        self.fetch_and_save_xray()

        # Pobierz i zapisz dane GOES (Primary i Secondary)
        self.fetch_and_save_goes()

        # Pobierz i zapisz obrazy SOHO/SDO
        self.fetch_and_save_solar_images()

        # Renderowanie dashboardu
        self.render_dashboard()


if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
