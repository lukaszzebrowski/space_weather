# 1. Obraz bazowy z Pythonem 3.12
FROM python:3.12-slim

# 2. Ustawienie katalogu roboczego
WORKDIR /app

# 3. Kopiowanie plików projektu do kontenera
COPY . /app

COPY .env /app/.env

ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

# 4. Instalacja zależności
RUN pip install --upgrade pip --root-user-action=ignore && pip install -r requirements.txt

# Instalacja bibliotek systemowych, w tym SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Otwarcie portu dla Streamlit
EXPOSE 8501

# 6. Uruchomienie aplikacji Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]