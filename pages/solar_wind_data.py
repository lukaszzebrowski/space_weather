import streamlit as st
import pandas as pd

from app.plot import DataPlot  # tam gdzie zdefiniowałeś create_solarwind_line_plot
from app.db_manager import DBManager  # jeśli używasz bazy


st.title("Dane wiatru słonecznego")
def show_solar_wind_data():
    # 1. Pobierz dane z bazy lub z API
    db = DBManager()
    rows = db.get_recent_solarwind(limit=None)

    # 2. Tworzymy DataFrame
    df_sw = pd.DataFrame(rows, columns=["ID", "time_tag", "proton_speed", "proton_density"])
    df_sw.drop(columns=["ID"], inplace=True, errors='ignore')

    # 3. Wykres prędkości
    fig_speed = DataPlot.create_solarwind_speed_line_plot(df_sw)
    if fig_speed:
        st.plotly_chart(fig_speed, use_container_width=True)

    # 4. Wykres gęstości
    fig_density = DataPlot.create_solarwind_density_line_plot(df_sw)
    if fig_density:
        st.plotly_chart(fig_density, use_container_width=True)


# Uruchomienie
show_solar_wind_data()