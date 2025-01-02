class DataProcessor:
    @staticmethod
    def filter_dscovr_data(data):
        """Filtruje dane tylko dla źródła DSCOVR."""
        return [item for item in data if item.get("source") == "DSCOVR"]

    @staticmethod
    def get_latest_data(data):
        """Zwraca najnowsze dane z DSCOVR."""
        if data:
            return data[-1]
        else:
            return None

    @staticmethod
    def process_radiation_data(data):
        """Przetwarza dane promieniowania rentgenowskiego."""
        if data:
            # Zakładamy, że dane są posortowane chronologicznie
            return data
        else:
            return []

    @staticmethod
    def get_latest_radiation_data(data):
        """Zwraca najnowszy pomiar promieniowania."""
        if data:
            return data[-1]
        else:
            return None
