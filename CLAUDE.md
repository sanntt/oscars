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

## Setup

```bash
poetry install
cp .env.example .env   # then fill in DATABASE_URL
alembic upgrade head
```

## Running

```bash
uvicorn oscars.api.main:app --reload
```

## Testing

```bash
poetry run pytest tests/unit/          # no database needed
poetry run pytest tests/integration/   # requires DATABASE_URL pointing to a test database
poetry run pytest --cov=src/oscars     # full coverage report
```

Integration tests require:
```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/oscars_test
```

## Conventions

- No comments. Code reads like a book.
- Domain entities are plain `@dataclass`. No SQLAlchemy in domain layer.
- Repository ABCs live in `domain/repositories.py`. Concrete implementations live in `infrastructure/`.
- `api/deps.py` is the only file that wires domain ABCs to infrastructure implementations.
- Date ranges use half-open intervals `[start_date, end_date)`.
- All monetary values use `Decimal`.
