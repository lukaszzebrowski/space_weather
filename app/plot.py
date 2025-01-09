import pandas as pd

class DataPlot:
    @staticmethod
    def create_table(data):
        """
        Tworzy tabelę (DataFrame) z aktualnymi danymi promieniowania (xray-flares-latest).
        Zwraca obiekt DataFrame, który można wyświetlić np. st.table(df).
        """
        df = pd.DataFrame(data)

        # Wybieramy kolumny z 'xray-flares-latest.json'
        # Przykładowa struktura:
        # {
        #   "time_tag": "2025-01-09T07:59:00Z",
        #   "satellite": 18,
        #   "current_class": "C1.0",
        #   "current_ratio": 0.0136,
        #   "current_int_xrlong": 0.0005970,
        #   "begin_time": "2025-01-09T04:29:00Z",
        #   "begin_class": "B7.8",
        #   "max_time": "Unk",
        #   "end_time": "Unk",
        #   "max_class": null,
        #   ...
        # }
        columns_to_show = [
            "time_tag",
            "satellite",
            "current_class",
            "current_ratio",
            "current_int_xrlong",
            "begin_time",

        ]
        # Upewnij się, że kolumny faktycznie istnieją w JSON — w razie braku niektórych,
        # możesz je dodać warunkowo lub pominąć
        df = df[columns_to_show]

        # Zmieniamy nazwy kolumn na bardziej czytelne
        df.rename(columns={
            "time_tag": "Aktualny czas pomiaru",
            "satellite": "Satelita",
            "current_class": "Aktualna klasa (X-Ray)",
            "current_ratio": "Ratio",
            "current_int_xrlong": "Natężenie XR-long",
            "begin_time": "Czas rozpoczęcia",

        }, inplace=True)

        return df
