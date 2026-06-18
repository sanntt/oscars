FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.4.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./
COPY src/ src/
COPY alembic.ini entrypoint.sh ./

RUN poetry install && rm -rf /tmp/poetry_cache && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
