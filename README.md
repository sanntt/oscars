# Oscars — Vehicle Inventory API

A REST API for managing a vehicle inventory and checking availability by date range. Vehicles can be marked as available or in maintenance. Available vehicles can be booked for a date range, and the system prevents double-bookings.

## Setup

[Docker Desktop](https://www.docker.com/products/docker-desktop/) is the only requirement. It includes Docker Compose, which runs both the API and the database.

```bash
docker compose up --build
```

The first time this runs it downloads images and installs dependencies, which takes a minute or two. Once you see `Application startup complete`, the API is ready.

- API base URL: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

The docs page lets you explore and call every endpoint from the browser without any extra tools.

### Running the tests

```bash
docker compose run --rm app pytest
```

This starts a temporary container, applies migrations, runs all tests, and removes the container when done. The main application does not need to be running.

### Stopping

```bash
docker compose down
```

To also delete the database and start fresh:

```bash
docker compose down -v
```

---

## Key design decisions

**Layered Clean Architecture.** The codebase is split into four layers: `domain`, `application`, `infrastructure`, and `api`. Each layer only imports from layers below it. Domain entities are plain Python dataclasses with no framework dependencies, which makes them easy to test and reason about in isolation. The `api/deps.py` file is the single crossing point where FastAPI's dependency injection wires the domain repository interfaces to their SQLAlchemy implementations.

**Repository pattern.** Abstract base classes in `domain/repositories.py` define what the application needs from persistence. The `infrastructure/` layer implements those contracts with SQLAlchemy. This means the application and domain layers have no knowledge of how data is stored, making it straightforward to swap the database or add an in-memory implementation for testing without touching any business logic.

**Two-layer overlap prevention.** Preventing double-bookings uses two complementary mechanisms. The application layer calls `find_overlapping()` before every booking and raises `OverlappingBookingError` immediately — this produces a clean 409 response under normal conditions. A PostgreSQL exclusion constraint (`EXCLUDE USING gist`) acts as a safety net at the database level and catches race conditions that slip through concurrent requests between the check and the insert. The repository catches the resulting `IntegrityError` and re-raises it as the same domain exception, so the caller always sees the same error regardless of which layer caught it.

**Half-open date intervals.** Date ranges follow the convention `[start_date, end_date)` — the start date is inclusive, the end date is exclusive. A booking from June 1 to June 5 occupies June 1, 2, 3, and 4. This is consistent at both the application level (overlap logic) and the database level (the `daterange` type in the exclusion constraint uses the same `[)` mode). Half-open intervals compose cleanly: two adjacent bookings like `[Jun 1, Jun 5)` and `[Jun 5, Jun 8)` never overlap.

**Price stored at booking time.** The booking price is calculated when the booking is created (`daily_price × days`) and stored on the booking record. This means the booking price is immutable — changing a vehicle's daily rate later does not affect past or future existing bookings.

**Decimal for money.** All monetary values use Python's `Decimal` type and PostgreSQL's `NUMERIC(10, 2)`. Floating-point types like `float` cannot represent currency values exactly and would introduce rounding errors.

---

## Tradeoffs

**Synchronous over asynchronous.** FastAPI and SQLAlchemy both have async support, but this implementation uses sync throughout. Async would improve throughput under high concurrency (many simultaneous requests) but adds significant complexity — async SQLAlchemy has different session semantics, and mixing sync and async code is a common source of subtle bugs. For this scope, sync is simpler, easier to reason about, and easier to test.

**Application-level overlap check redundancy.** The database exclusion constraint alone would be sufficient to prevent double-bookings. The application-level `find_overlapping()` check exists so that the common case (non-concurrent conflict) produces a clean domain error without needing to parse a database exception. The tradeoff is a small extra query on every booking creation. Under very high write concurrency, both checks could be considered and the application-level check offers no race-condition protection on its own.

**Price not recalculated on read.** Storing the price at booking time means the bookings table holds data that could be derived. The benefit is that the price is stable — it does not change if a vehicle's daily rate is updated. The tradeoff is that if you need to audit pricing (e.g., apply a discount after the fact), you need to update the stored value explicitly rather than changing the rate.

**Exclusive bookings only.** A vehicle can have at most one booking for any given date range. There is no concept of booking types, quantities, or partial availability. This matches the stated requirements but would need to change if vehicles could be shared or if multiple booking categories existed (e.g., reserved vs. confirmed).

---

## What I'd do differently in production

**Authentication and authorisation.** There is currently no auth layer. Any caller can create vehicles, update statuses, or create bookings. In production, endpoints that modify state would require authentication (e.g., JWT or OAuth 2.0) and role-based access control to separate, for example, fleet managers from customers.

**Input validation.** The current Pydantic schemas accept any `Decimal` for `daily_price` and any date pair for bookings. Production schemas would reject negative prices, enforce a minimum booking duration, and optionally reject bookings starting in the past.

**Pagination.** `GET /vehicles` returns all records. For a real fleet, this endpoint would need pagination or cursor-based iteration to avoid loading thousands of rows into memory.

**Observability.** The application has no structured logging, metrics, or distributed tracing. In production I would add structured JSON logs with request IDs, Prometheus metrics for latency and error rates, and traces (e.g., OpenTelemetry) to diagnose slow queries.

**Connection pooling.** The current setup creates a new SQLAlchemy engine with default pool settings. Under load, this would need tuning (pool size, overflow, timeout) and likely a connection pooler like PgBouncer in front of PostgreSQL.

**Secrets management.** The database URL is passed as an environment variable, which works but is not auditable. In production, credentials would be fetched from a secrets manager (AWS Secrets Manager, HashiCorp Vault) at startup rather than injected as plain-text environment variables.

**Migration strategy.** Alembic migrations run inside the container entrypoint, which means every deployment applies migrations before the server starts. This is fine for a single instance but creates a coordination problem when running multiple replicas — migrations should be a separate deployment step with a lock to prevent parallel runs.

**Booking lifecycle.** There is no cancellation, modification, or status tracking on bookings. A production system would need cancellation logic, possibly with refund rules, and an audit trail of state changes.

---

## Assumptions

- A vehicle can only have one active booking for any given period. Bookings are exclusive and do not overlap.
- The booking price is fixed at the time of creation. Changing a vehicle's daily rate does not affect existing bookings.
- End date must be strictly after start date. Same-day bookings (zero duration) are not allowed.
- There is no concept of users or customers. Bookings are not associated with who made them.
- Vehicles are never deleted — only their status changes between `available` and `maintenance`.
- An `available` vehicle with an existing booking in a requested date range is treated as unavailable for that range, even though its status field still reads `available`.
- The `btree_gist` PostgreSQL extension is available. It is included in standard PostgreSQL distributions but may need to be enabled explicitly on some managed database platforms.
