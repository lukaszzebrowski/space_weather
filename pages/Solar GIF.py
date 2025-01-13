# pages/SolarGIF.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from app.db_manager import DBManager
from app.gif_utils import create_gif_in_memory

def show_solar_gif_page():
    st.title("Tworzenie GIF-a (Pillow) z bazy")

    db = DBManager()  # obiekt bazy

    # 1) Wybór źródeł
    possible_sources = ["SOHO LASCO C2", "SOHO LASCO C3", "SDO HMI Continuum"]
    source = st.selectbox("Wybierz źródło:", possible_sources)

    # 2) Wybór zakresu dat
    end_date_default = date.today()
    start_date_default = end_date_default - timedelta(days=1)

    date_range = st.date_input(
        "Zakres dat (Od – Do):",
        value=(start_date_default, end_date_default)
    )
    if len(date_range) != 2:
        st.warning("Wybierz dwie daty (początkową i końcową).")
        return

    start_date, end_date = date_range
    if end_date < start_date:
        st.warning("Data końcowa jest wcześniejsza niż początkowa!")
        return

    # Konwersja do stringów w formacie 'YYYY-MM-DD HH:MM:SS'
    start_str = f"{start_date} 00:00:00"
    end_str   = f"{end_date} 23:59:59"

    # 3) Czas klatki w ms (Pillow używa milisekund)
    frame_ms = st.slider(
        "Czas każdej klatki (ms):",
        min_value=100, max_value=5000, value=500, step=100
    )

    # 4) Tworzymy GIF po kliknięciu
    if st.button("Utwórz GIF"):
        rows = db.get_solar_images_for_sources_in_range(start_str, end_str, [source])
        if not rows:
            st.warning("Brak obrazów w wybranym przedziale.")
            return

        # rows to list krotek: (source, image, time_tag)
        df = pd.DataFrame(rows, columns=["source", "image", "time_tag"])
        # Parsowanie time_tag => datetime, sortowanie rosnąco
        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce")
        df = df.sort_values("time_tag")

        images_data_list = df["image"].tolist()  # kolumna BLOB
        if len(images_data_list) < 2:
            st.warning("Znaleziono tylko 1 klatkę – animacja się nie uda.")
            return

        # 5) Tworzymy GIF w pamięci
        gif_buffer = create_gif_in_memory(images_data_list, duration_ms=frame_ms)
        if gif_buffer is None:
            st.error("Nie udało się utworzyć GIF-a (za mało klatek?).")
        else:
            st.success("GIF utworzony w pamięci (Pillow).")
            # 6) Wyświetlamy z pamięci
            st.image(gif_buffer, caption=f"Animacja z {source}", use_container_width=True)

# Rejestrujemy stronę w Streamlit
show_solar_gif_page()
