import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

def create_gauge(speed, density, time_tag):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=speed,
        title={'text': f"Prędkość protonów: <b>{speed}(km/s)</b><br>"
                       f"Gęstość protonów: <b>{density} protons/cm3</b><br>"
                       f"Ostatni pomiar: <b>{time_tag}</b>",
               'font': {'size': 30}
               },
        gauge={
            'axis': {'range': [0, 1000], 'tickwidth': 1, 'tickcolor': "darkblue", 'dtick': 50},
            'bar': {'color': "orange"},
            'steps': [
                {'range': [0, 300], 'color': "green"},
                {'range': [300, 600], 'color': "yellow"},
                {'range': [600, 1000], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': speed
            }
        }
    ))
    fig.update_layout(
        autosize=False,
        width=1000,  # zwiększ szerokość
        height=700,  # zwiększ wysokość
        margin=dict(l=80, r=80, t=50, b=50)  # dostosuj marginesy
    )
    return fig

st.set_page_config(layout="wide")

# Automatyczne odświeżanie co 60 sekund (60000 ms)
st_autorefresh(interval=60000, limit=None, key="data_refresh")

st.markdown("<h1 style='text-align: center;'>Dashboard pogody kosmicznej</h1>", unsafe_allow_html=True)

# URL API NOAA
url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    dscovr_data = [item for item in data if item.get("source") == "DSCOVR"]

    if dscovr_data:
        # Pobieramy najświeższy wpis z DSCOVR
        latest_dscovr_data = dscovr_data[-1]
        source = latest_dscovr_data.get("source", None)
        proton_speed = latest_dscovr_data.get("proton_speed", None)
        time_tag = latest_dscovr_data.get("time_tag", "Brak danych")
        density = latest_dscovr_data.get("proton_density", None)

        if proton_speed is not None:

            gauge_fig = create_gauge(proton_speed, density, time_tag)

            col1, col2 = st.columns([2, 3])

            with col1:
                st.title("Monitor Wiatru Słonecznego")
                st.markdown(f"### Dane z satelity **{source}**")
                st.plotly_chart(gauge_fig, use_container_width=True)

            with col2:
                st.image("https://sdo.gsfc.nasa.gov/assets/img/latest/latest_4096_HMIIC.jpg",
                         caption="Obraz Słońca z SDO")
        else:
            st.error("Brak danych o prędkości protonów.")
else:
    st.error("Błąd podczas pobierania danych z API. Sprawdź połączenie internetowe lub URL API.")

last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"<h4 style='text-align: right;'>Ostatnie odświeżenie: {last_refresh}</h4>", unsafe_allow_html=True)


