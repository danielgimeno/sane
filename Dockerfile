# --- Frontend build ---
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# --- Backend runtime ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main --no-root

COPY sae/ sae/
COPY --from=frontend /app/frontend/dist frontend/dist

RUN poetry install --only main

EXPOSE 8000

CMD ["uvicorn", "sae.main:app", "--host", "0.0.0.0", "--port", "8000"]
