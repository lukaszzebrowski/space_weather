import streamlit as st
from streamlit_autorefresh import st_autorefresh
from app.api import NOAADataFetcher, RadiationDataFetcher, XRayDataFetcher
from app.gauge import GaugePlot
from app.utils import DataProcessor
from app.plot import DataPlot
from datetime import datetime

# Konfiguracja strony MUSI być pierwszym wywołaniem Streamlit
st.set_page_config(
    layout="wide",
    page_title="Dashboard Pogody Kosmicznej",
    page_icon="🌌"
)

class SpaceWeatherDashboard:
    def __init__(self):
        # URL do danych wiatru słonecznego
        self.api_url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
        self.fetcher = NOAADataFetcher(self.api_url)
        self.processor = DataProcessor()
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # URL do danych promieniowania rentgenowskiego
        self.radiation_url = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"
        self.radiation_fetcher = RadiationDataFetcher(self.radiation_url)

        # URL do danych promieniowania z 7 dni
        self.xray_7day_url = "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json"
        self.xray_7day_fetcher = XRayDataFetcher(self.xray_7day_url)

    def fetch_and_process_data(self):
        """Pobiera i przetwarza dane z API."""
        try:
            # Pobieranie danych wiatru słonecznego
            raw_data = self.fetcher.fetch_data()
            dscovr_data = self.processor.filter_dscovr_data(raw_data)
            latest_data = self.processor.get_latest_data(dscovr_data)

            # Pobieranie danych promieniowania rentgenowskiego
            radiation_raw_data = self.radiation_fetcher.fetch_data()
            radiation_data = self.processor.process_radiation_data(radiation_raw_data)
            latest_radiation = self.processor.get_latest_radiation_data(radiation_data)

            # Pobieranie danych promieniowania z 7 dni
            xray_7day_data = self.xray_7day_fetcher.fetch_data()

            return latest_data, radiation_data, latest_radiation, xray_7day_data
        except Exception as e:
            st.error(f"Błąd podczas pobierania danych: {str(e)}")
            return None, None, None, None

    def render_dashboard(self, latest_data, radiation_data, latest_radiation, xray_7day_data):
        """Renderuje główny layout dashboardu."""
        st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)

        # Wyświetlenie czasu ostatniego odświeżenia
        st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {self.last_refresh}</h4>",
                    unsafe_allow_html=True)

        if latest_data:
            proton_speed = latest_data.get("proton_speed", None)
            proton_density = latest_data.get("proton_density", None)
            time_tag = latest_data.get("time_tag", "Brak danych")


            gauge_fig = GaugePlot.create_gauge(proton_speed, proton_density, time_tag)
            col1, col2 = st.columns([2, 2])

            with col1:
                st.image(
                    "https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg",
                    caption="Obraz Słońca z SOHO (LASCO C2)"
                )
                st.title("Monitor Wiatru Słonecznego")
                st.plotly_chart(gauge_fig, use_container_width=True, key="solar_wind_gauge")

            with col2:
                st.image(
                    "https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg",
                    caption="Obraz Słońca z SOHO (LASCO C3)"
                )
                # Wyświetlenie wykresu promieniowania z 7 dni
                if xray_7day_data:
                    st.subheader("Promieniowanie rentgenowskie (7 dni)")
                    xray_7day_plot = DataPlot.create_7_day_xray_plot(xray_7day_data)
                    st.plotly_chart(xray_7day_plot, use_container_width=True, key="xray_7day_plot")

        else:
            st.error("Brak danych z satelity DSCOVR.")




    def run(self):
        """Uruchamia aplikację Streamlit."""
        # Aktualizacja czasu ostatniego odświeżenia
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Automatyczne odświeżanie co 60 sekund
        st_autorefresh(interval=60000, limit=None, key="data_refresh")

        # Pobranie i przetworzenie danych
        latest_data, radiation_data, latest_radiation, xray_7day_data = self.fetch_and_process_data()

        # Renderowanie dashboardu
        self.render_dashboard(latest_data, radiation_data, latest_radiation, xray_7day_data)

if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
