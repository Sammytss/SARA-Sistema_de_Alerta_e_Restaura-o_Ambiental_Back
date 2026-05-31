FROM python:3.12-slim

WORKDIR /app

# Todos os pacotes usam wheels pré-compiladas (psycopg2-binary, bcrypt, cryptography)
# Não requer gcc nem libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p storage

EXPOSE 8000

# Prod: Gunicorn gerenciando workers Uvicorn
# Dev: substituído pelo comando no docker-compose (hot-reload com uvicorn --reload)
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120"]
