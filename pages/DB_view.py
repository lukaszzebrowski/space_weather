import streamlit as st
import pandas as pd
from app.db_manager import DBManager  # Upewnij się, że import jest poprawny

def show_database_contents():
    st.subheader("Podgląd zawartości bazy danych")

    # Inicjalizacja bazy danych
    db = DBManager()

    # Wybór tabeli
    table_choice = st.selectbox("Wybierz tabelę do podglądu:", ["xray", "solarwind", "solar_images", "goes_data"])

    # Pobranie danych
    rows, columns = db.get_all_from_table(table_choice)

    # Wyświetlenie danych jako DataFrame
    if rows:
        df = pd.DataFrame(rows, columns=columns)

        # Jeśli wybrano tabelę 'goes_data', formatujemy kolumny w notacji wykładniczej
        if table_choice == "goes_data":
            scientific_columns = ["flux", "observed_flux", "electron_correction"]

            # Sprawdzamy, czy kolumny istnieją w df i formatujemy
            for col in scientific_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"{x:.2e}" if pd.notnull(x) else x)

        st.dataframe(df)
    else:
        st.info(f"Brak danych w tabeli: {table_choice}")

# Uruchomienie podglądu bazy
show_database_contents()
