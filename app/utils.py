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
    def process_xray_latest_data(data):
        """
        Jeśli trzeba, przetwarzaj dane z xray-flares-latest,
        np. sortuj, wycinaj brakujące wartości, itd.
        Tu możesz też wybrać najnowszy wpis, jeśli JSON zawiera listę >1.
        """
        if data:
            return data
        else:
            return []

    @staticmethod
    def get_latest_xray_measure(data):
        """Zwraca najnowszy (ostatni) wpis z listy x-ray, jeśli istnieje."""
        if data:
            return data[-1]
        return None