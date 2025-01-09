import pandas as pd

class DataPlot:
    @staticmethod
    def create_xray_table(data):
        """
        Tworzy DataFrame z danymi X-Ray i zwraca go,
        posortowany według time_tag (od najstarszego do najnowszego),
        a następnie formatuje kolumnę time_tag jako "YYYY-MM-DD HH:MM:SS" bez strefy czasowej.

        data to lista krotek: (id, time_tag, satellite, current_class,
                               current_ratio, current_int_xrlong, begin_time)
        """
        df = pd.DataFrame(data, columns=[
            "ID",
            "time_tag",
            "satellite",
            "current_class",
            "current_ratio",
            "current_int_xrlong",
            "begin_time"
        ])

        # Usuwamy kolumnę ID, jeśli nie chcesz jej wyświetlać
        df.drop(columns=["ID"], inplace=True)

        # 1) Konwersja na datetime (z interpretacją ewentualnej strefy jako UTC)
        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce", utc=True)

        # 2) Usuwamy strefę czasową, staje się „naiwny” czas
        df["time_tag"] = df["time_tag"].dt.tz_localize(None)

        # 3) Sortowanie rosnąco po time_tag (najstarsze na górze)
        df.sort_values("time_tag", ascending=True, inplace=True)

        # 4) Formatowanie do "YYYY-MM-DD HH:MM:SS"
        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)  # Ustawiamy puste etykiety dla każdego wiersza

        return df

    @staticmethod
    def create_solarwind_table(data):
        """
        Tworzy DataFrame z danymi wiatru słonecznego i zwraca go,
        posortowany według time_tag (od najstarszego do najnowszego),
        a następnie formatuje kolumnę time_tag jako "YYYY-MM-DD HH:MM:SS" bez strefy czasowej.

        data to lista krotek: (id, time_tag, proton_speed, proton_density)
        """
        df = pd.DataFrame(data, columns=[
            "ID",
            "time_tag",
            "proton_speed",
            "proton_density"
        ])

        df.drop(columns=["ID"], inplace=True)

        # Konwersja na datetime z interpretacją strefy jako UTC
        df["time_tag"] = pd.to_datetime(df["time_tag"], errors="coerce", utc=True)

        # Usunięcie strefy (tz_localize(None))
        df["time_tag"] = df["time_tag"].dt.tz_localize(None)

        # Sortowanie rosnąco
        df.sort_values("time_tag", ascending=True, inplace=True)

        # Formatowanie
        df["time_tag"] = df["time_tag"].dt.strftime("%d-%m-%Y %H:%M")
        df.index = [""] * len(df)  # Ustawiamy puste etykiety dla każdego wiersza

        return df
