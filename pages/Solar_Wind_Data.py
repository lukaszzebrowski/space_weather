import streamlit as st
import pandas as pd

from app.plot import DataPlot
from app.db_manager import DBManager


st.title("Dane wiatru słonecznego")
def show_solar_wind_data():
    db = DBManager()
    rows = db.get_recent_solarwind(limit=None)

    df_sw = pd.DataFrame(rows, columns=["ID", "time_tag", "proton_speed", "proton_density", "proton_temperature"])
    df_sw.drop(columns=["ID"], inplace=True, errors='ignore')

    fig_speed = DataPlot.create_solarwind_speed_line_plot(df_sw)
    if fig_speed:
        st.plotly_chart(fig_speed, use_container_width=True)

    fig_density = DataPlot.create_solarwind_density_line_plot(df_sw)
    if fig_density:
        st.plotly_chart(fig_density, use_container_width=True)

    fig_temp = DataPlot.create_solarwind_temp_line_plot(df_sw)
    if fig_temp:
        st.plotly_chart(fig_temp, use_container_width=True)


show_solar_wind_data()