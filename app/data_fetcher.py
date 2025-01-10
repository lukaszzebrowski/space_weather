import requests
from dotenv import load_dotenv
import os

# Załaduj zmienne z pliku .env
load_dotenv()

class NOAADataFetcher:
    """
    Pobiera dane wiatru słonecznego (DSCOVR).
    """
    def __init__(self, url="https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"):
        self.url = url

    def fetch_data(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data  # lista pomiarów

class XRayDataFetcher:
    """
    Pobiera dane X-Ray z xray-flares-latest.json
    (zazwyczaj 1-elementowa lista).
    """
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"):
        self.url = url

    def fetch_data(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data  # lista (zwykle 1 lub kilka wpisów)

class APODDataFetcher:
    def __init__(self, api_url="https://api.nasa.gov/planetary/apod"):
        self.api_url = api_url
        self.api_key = os.getenv("NASA_API_KEY")  # Pobierz klucz API podczas inicjalizacji klasy

    def fetch_background_image_url(self):
        """
        Pobiera URL zdjęcia z NASA APOD.
        """
        params = {"api_key": self.api_key}
        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("hdurl", "")  # Pobierz URL zdjęcia

class GOESPrimaryFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"):
        self.url = url

    def fetch_data(self):
        """Pobiera dane GOES Primary."""
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data  # Zwraca dane jako listę słowników

class GOESSecondaryFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/secondary/xrays-1-day.json"):
        self.url = url

    def fetch_data(self):
        """Pobiera dane GOES Secondary."""
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data  # Zwraca dane jako listę słowników