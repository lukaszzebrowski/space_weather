import requests

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
