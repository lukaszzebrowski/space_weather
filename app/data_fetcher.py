import requests
from dotenv import load_dotenv
import hashlib
from datetime import datetime

load_dotenv()

class NOAADataFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"):
        self.url = url

    def fetch_data(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data

class XRayDataFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json"):
        self.url = url

    def fetch_data(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data


class GOESPrimaryFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"):
        self.url = url

    def fetch_data(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data

class GOESSecondaryFetcher:
    def __init__(self, url="https://services.swpc.noaa.gov/json/goes/secondary/xrays-1-day.json"):
        self.url = url

    def fetch_data(self):
        """Pobiera dane GOES Secondary."""
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data

class SolarImageFetcher:
    def __init__(self):
        self.image_sources = {
            "SOHO LASCO C2": "https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg",
            "SOHO LASCO C3": "https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg",
            "SDO HMI Continuum": "https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg"
        }

    @staticmethod
    def calculate_image_hash(image_data):
        return hashlib.sha256(image_data).hexdigest()

    def fetch_images(self):
        images = []
        for source_name, url in self.image_sources.items():
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                image_data = response.content
                image_hash = self.calculate_image_hash(image_data)
                time_tag = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                images.append({
                    "source": source_name,
                    "image_data": image_data,
                    "image_hash": image_hash,
                    "time_tag": time_tag
                })
            except Exception as e:
                print(f"Błąd pobierania obrazu z {source_name}: {e}")
        return images
