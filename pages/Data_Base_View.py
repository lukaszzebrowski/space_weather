import streamlit as st
import pandas as pd
from app.db_manager import DBManager

def show_database_contents():
    st.subheader("Podgląd zawartości bazy danych")

    db = DBManager()

    table_choice = st.selectbox("Wybierz tabelę do podglądu:", ["xray", "solarwind", "solar_images", "goes_data"])

    rows, columns = db.get_all_from_table(table_choice)

    if rows:
        df = pd.DataFrame(rows, columns=columns)

        if table_choice == "goes_data":
            scientific_columns = ["flux", "observed_flux", "electron_correction"]

            for col in scientific_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"{x:.2e}" if pd.notnull(x) else x)

        st.dataframe(df)
    else:
        st.info(f"Brak danych w tabeli: {table_choice}")

show_database_contents()
