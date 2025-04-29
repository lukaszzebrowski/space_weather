FROM python:3.12-slim

WORKDIR /app

COPY . /app

COPY .env /app/.env

RUN pip install --upgrade pip --root-user-action=ignore && pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]