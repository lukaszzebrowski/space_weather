from dotenv import load_dotenv
import os

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv(dotenv_path=".env")

# Pobierz klucz API
NASA_API_KEY = os.getenv("NASA_API_KEY")
print(NASA_API_KEY)  # Sprawdź, czy klucz jest poprawnie wczytany
