FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace/services/ia
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

FROM base AS test
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
COPY pytest.ini ./
RUN python -m pytest -v

FROM base AS runtime
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
