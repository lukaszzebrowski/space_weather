import requests

class SolarWindDataFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"):
        self.url = url

    def fetch_data(self):
        """
        Zwraca listę danych wiatru słonecznego (JSON).
        Bierzemy [-1], by uzyskać najnowszy pomiar.
        """
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        data = resp.json()  # lista słowników
        return data

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
