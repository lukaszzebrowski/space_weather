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
