# Oscars — Vehicle Inventory System

## Architecture

Strict layered Clean Architecture. No layer imports from a layer above it.

```
src/oscars/
  domain/          Pure Python entities, repository ABCs, domain exceptions. No framework deps.
  application/     Use case functions. Imports domain only.
  infrastructure/  SQLAlchemy ORM models, concrete repositories, DB session, Alembic migrations.
  api/             FastAPI routers, Pydantic schemas, dependency injection wiring.
tests/
  unit/            Mock repositories, no database required.
  integration/     Real PostgreSQL, real FastAPI test client.
```

## First-time Setup

### With Docker (recommended)

Requires Docker and Docker Compose.

```bash
docker compose up --build
```

This starts PostgreSQL, runs all pending migrations, and launches the API on http://localhost:8000.

API docs are available at http://localhost:8000/docs once the app is running.

To stop and remove volumes:

```bash
docker compose down -v
```

### Without Docker (local development)

Requires Python 3.12+, Poetry, and a running PostgreSQL instance.

```bash
# Install dependencies
poetry install

# Configure the database connection
cp .env.example .env
# Edit .env and set DATABASE_URL to point to your PostgreSQL instance

# Apply migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn oscars.api.main:app --reload
```

API docs are available at http://localhost:8000/docs.

## Running Tests

```bash
docker compose run --rm app pytest
```

`src/` and `tests/` are mounted as volumes via `docker-compose.override.yml`, so local changes are picked up immediately without rebuilding the image.

To run only unit tests (no database needed):
```bash
docker compose run --rm app pytest tests/unit/
```

## Definition of Done

Every feature is only complete when all three of the following pass with no errors. Fix any failure before committing.

**1. Format**
```bash
docker compose run --rm app ruff format src/ tests/
```

**2. Lint**
```bash
docker compose run --rm app ruff check src/ tests/
```

**3. Tests**
```bash
docker compose run --rm app pytest
```

If working locally without Docker:
```bash
poetry run ruff format src/ tests/
poetry run ruff check src/ tests/
poetry run pytest
```

## Bruno API Collection

The `bruno/` directory contains a Bruno collection for manually exercising the API. When adding or changing an endpoint, update the corresponding `.bru` file (or add a new one). Each file maps to one request: method, URL, path params, headers, and body.

## Conventions

- No comments. Code reads like a book.
- Domain entities are plain `@dataclass`. No SQLAlchemy in domain layer.
- Repository ABCs live in `domain/repositories.py`. Concrete implementations live in `infrastructure/`.
- `api/deps.py` is the only file that wires domain ABCs to infrastructure implementations.
- Date ranges use half-open intervals `[start_date, end_date)`.
- All monetary values use `Decimal`.
