FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    curl \
    iputils-ping \
    && pip install poetry \
    && apt-get purge -y --auto-remove gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml poetry.lock ./
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:$PATH"
RUN poetry install --only main --no-root
COPY . .
CMD ["/bin/sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
EXPOSE 8000