import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("Historia prędkości wiatru słonecznego")

# Pobranie danych z NOAA
url = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Konwersja danych do DataFrame
    df = pd.DataFrame(data)

    # Sprawdzamy czy kolumny istnieją
    if "time_tag" in df.columns and "proton_speed" in df.columns:
        # Konwersja kolumny z czasem na typ datetime
        df['time_tag'] = pd.to_datetime(df['time_tag'])

        # Sortowanie danych wg czasu
        df = df.sort_values('time_tag')

        # Usunięcie nulli lub wartości None w prędkości
        df = df.dropna(subset=['proton_speed'])

        # Przedział czasowy danych
        min_date = df['time_tag'].min()
        max_date = df['time_tag'].max()

        st.write(f"Dane dostępne od {min_date} do {max_date} UTC")

        # Suwak do wyboru zakresu dat
        # Konwertujemy daty na format potrzebny w sliderze (np. całe dni)
        start_date = st.slider("Wybierz datę początkową",
                               min_value=min_date.to_pydatetime(),
                               max_value=max_date.to_pydatetime(),
                               value=min_date.to_pydatetime())

        end_date = st.slider("Wybierz datę końcową",
                             min_value=min_date.to_pydatetime(),
                             max_value=max_date.to_pydatetime(),
                             value=max_date.to_pydatetime())

        # Filtracja danych wg wybranego zakresu
        mask = (df['time_tag'] >= pd.to_datetime(start_date)) & (df['time_tag'] <= pd.to_datetime(end_date))
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("Brak danych w wybranym przedziale czasowym.")
        else:
            # Tworzenie wykresu liniowego
            fig = px.line(filtered_df, x='time_tag', y='proton_speed', title='Prędkość protonów w funkcji czasu',
                          labels={'time_tag': 'Czas (UTC)', 'proton_speed': 'Prędkość (km/s)'})
            fig.update_xaxes(rangeslider_visible=True)  # dodanie suwaka czasu w dolnej osi wykresu
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("W danych brakuje wymaganych kolumn 'time_tag' lub 'proton_speed'.")
else:
    st.error("Błąd podczas pobierania danych z API. Sprawdź połączenie internetowe lub URL API.")
