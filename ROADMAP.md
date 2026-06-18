# Roadmap

Seven self-contained iterations. Each ships as its own PR with minimal features and full tests.

- [x] **Iteration 1 — Bootstrap**: Empty project skeleton, CLAUDE.md, ROADMAP.md, pyproject.toml, Alembic config, Dockerfile and Docker Compose for self-contained local execution.
- [x] **Iteration 2 — Vehicle domain model + create**: `Vehicle` entity, `VehicleStatus` enum, `VehicleRepository` ABC, `create_vehicle` use case, SQLAlchemy model, migration, unit + integration tests.
- [x] **Iteration 3 — Vehicle status change**: `update_vehicle_status` use case, AVAILABLE ↔ MAINTENANCE transitions, tests.
- [ ] **Iteration 4 — Available vehicles endpoint**: `GET /vehicles?start_date=&end_date=` returns non-maintenance vehicles. FastAPI router + Pydantic schemas + endpoint tests.
- [ ] **Iteration 5 — Booking domain model + create**: `Booking` entity, `BookingRepository` ABC, `create_booking` use case with maintenance guard and price calculation, migration, unit + integration tests.
- [ ] **Iteration 6 — Booking creation endpoint**: `POST /bookings`, error handling, endpoint tests.
- [ ] **Iteration 7 — Overlap prevention**: Application-level overlap check + PostgreSQL exclusion constraint (`btree_gist`) for concurrent request safety. Full edge-case tests.

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Framework | FastAPI (sync) | Type-safe, auto-docs, clean DI — avoids async complexity |
| Database | PostgreSQL | Exclusion constraints for concurrent booking prevention |
| ORM | SQLAlchemy (sync) | Clean repository abstraction, Alembic migrations |
| Package manager | Poetry | Lock-file based, clean `pyproject.toml` |
| Architecture | Layered Clean Architecture | SOLID-compliant, domain stays pure Python |
| Date range | Half-open `[start, end)` | Consistent semantics at app and DB level |
| Money | `Decimal` + `NUMERIC(10,2)` | No floating-point rounding errors |
| Concurrent booking | DB exclusion constraint + app-level check | DB is the final guard; app check provides a clean error before hitting the constraint |
| Test isolation | Savepoint rollback per test | Fast: no table recreation per test |
