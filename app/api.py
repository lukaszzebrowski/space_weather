import requests

class NOAADataFetcher:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        """Pobiera dane z API NOAA."""
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Błąd podczas pobierania danych z API.")

class RadiationDataFetcher:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        """Pobiera dane promieniowania rentgenowskiego."""
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Błąd podczas pobierania danych promieniowania.")

class XRayDataFetcher:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        """Pobiera dane promieniowania rentgenowskiego (bieżące) z xray-flares-latest."""
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Błąd podczas pobierania danych z API xray-flares-latest.")
