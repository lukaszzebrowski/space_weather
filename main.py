import streamlit as st
from streamlit_autorefresh import st_autorefresh
from app.api import NOAADataFetcher
from app.gauge import GaugePlot
from app.utils import DataProcessor
from datetime import datetime


class SpaceWeatherDashboard:
    def __init__(self):
        self.api_url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
        self.fetcher = NOAADataFetcher(self.api_url)
        self.processor = DataProcessor()
        self.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def fetch_and_process_data(self):
        """Pobiera i przetwarza dane z API."""
        try:
            raw_data = self.fetcher.fetch_data()
            dscovr_data = self.processor.filter_dscovr_data(raw_data)
            return self.processor.get_latest_data(dscovr_data)
        except Exception as e:
            st.error(f"Błąd podczas pobierania danych: {str(e)}")
            return None

    def render_dashboard(self, latest_data):
        """Renderuje główny layout dashboardu."""
        if latest_data:
            proton_speed = latest_data.get("proton_speed", None)
            proton_density = latest_data.get("proton_density", None)
            time_tag = latest_data.get("time_tag", "Brak danych")

            if proton_speed is not None:
                gauge_fig = GaugePlot.create_gauge(proton_speed, proton_density, time_tag)

                col1, col2 = st.columns([3, 3])

                with col1:
                    st.image(
                        "https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg",
                        caption="Obraz Słońca z SOHO (LASCO C2)"
                    )
                    st.title("Monitor Wiatru Słonecznego")
                    st.markdown(f"### Dane z satelity **{latest_data.get('source', 'Brak danych')}**")
                    st.plotly_chart(gauge_fig, use_container_width=True)

                with col2:
                    st.image(
                        "https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg",
                        caption="Obraz Słońca z SOHO (LASCO C3)"
                    )
            else:
                st.error("Brak danych o prędkości protonów.")
        else:
            st.error("Brak danych z satelity DSCOVR.")

        st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {self.last_refresh}</h4>", unsafe_allow_html=True)

    def run(self):
        """Uruchamia aplikację Streamlit."""
        st.set_page_config(layout="wide")

        # Automatyczne odświeżanie co 60 sekund
        st_autorefresh(interval=60000, limit=None, key="data_refresh")

        st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)

        # Fetch and process data
        latest_data = self.fetch_and_process_data()

        # Render the dashboard
        self.render_dashboard(latest_data)

if __name__ == "__main__":
    app = SpaceWeatherDashboard()
    app.run()
