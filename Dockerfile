FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COUGHGPT_BACKEND_URL=http://127.0.0.1:8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
COPY frontend/requirements.txt /app/frontend/requirements.txt

RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install --no-cache-dir -r /app/frontend/requirements.txt

COPY . /app

EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0"]
