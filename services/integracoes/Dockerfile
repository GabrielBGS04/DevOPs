FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 B1_DB_PATH=/data/integracoes.sqlite3
WORKDIR /workspace/services/integracoes
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

FROM base AS test
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
COPY pytest.ini ./
RUN python -m pytest -v

FROM base AS runtime
VOLUME ["/data"]
EXPOSE 8002
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
