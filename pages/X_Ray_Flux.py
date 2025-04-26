import streamlit as st
import pandas as pd

from app.plot import DataPlot
from app.db_manager import DBManager

st.title("Natężenie promieniowania X-Ray (GOES)")

def show_x_ray_flux_data():
    db = DBManager()
    rows = db.get_recent_goes_data(limit=None)

    if not rows:
        st.warning("Brak danych GOES w bazie.")
        return

    df_sw = pd.DataFrame(rows, columns=[
        "id",
        "time_tag",
        "satellite",
        "flux",
        "observed_flux",
        "electron_correction",
        "electron_contamination",
        "energy"
    ])

    df_sw.drop(columns=["id"], inplace=True, errors='ignore')

    fig_x_ray_flux = DataPlot.create_goes_flux_line_plot(df_sw)
    if fig_x_ray_flux:
        st.plotly_chart(fig_x_ray_flux, use_container_width=True)
    else:
        st.warning("Brak danych do wyświetlenia wykresu.")


show_x_ray_flux_data()
