import streamlit as st
import pandas as pd

from app.plot import DataPlot  # Zakładamy, że tutaj jest funkcja create_goes_flux_line_plot
from app.db_manager import DBManager

st.title("Natężenie promieniowania X-Ray (GOES)")

def show_x_ray_flux_data():
    # 1. Pobierz dane z bazy
    db = DBManager()
    rows = db.get_recent_goes_data(limit=None)

    # 2. Sprawdzenie, czy dane istnieją
    if not rows:
        st.warning("Brak danych GOES w bazie.")
        return

    # 3. Tworzenie DataFrame z poprawnymi kolumnami
    df_sw = pd.DataFrame(rows, columns=[
        "id",  # Dodano kolumnę ID
        "time_tag",
        "satellite",
        "flux",
        "observed_flux",
        "electron_correction",
        "electron_contamination",
        "energy"
    ])

    # 4. Usunięcie kolumny ID (jeśli niepotrzebna)
    df_sw.drop(columns=["id"], inplace=True, errors='ignore')

    # 5. Tworzenie wykresu
    fig_x_ray_flux = DataPlot.create_goes_flux_line_plot(df_sw)
    if fig_x_ray_flux:
        st.plotly_chart(fig_x_ray_flux, use_container_width=True)
    else:
        st.warning("Brak danych do wyświetlenia wykresu.")

# 6. Uruchomienie funkcji
show_x_ray_flux_data()
