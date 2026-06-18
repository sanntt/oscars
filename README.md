# Oscars — Vehicle Inventory API

A REST API for managing a vehicle inventory and checking availability by date range. Vehicles can be marked as available or in maintenance. Available vehicles can be booked for a date range, and the system prevents double-bookings.

## Requirements

[Docker Desktop](https://www.docker.com/products/docker-desktop/) — that is all you need. Docker Desktop includes Docker Compose, which is used to run both the application and its database.

## Running the application

Open a terminal in the project folder and run:

```bash
docker compose up --build
```

The first time this runs it will download the necessary images and install dependencies, which takes a minute or two. Once you see a line like `Application startup complete`, the API is ready.

- API base URL: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

The docs page lets you explore and call every endpoint directly from the browser — no extra tools needed.

## Running the tests

The application does not need to be running. Open a terminal in the project folder and run:

```bash
docker compose run --rm app pytest
```

This starts a temporary container, applies any pending migrations, runs all tests against the database, and removes the container when done.

## Stopping the application

Press `Ctrl+C` in the terminal where `docker compose up` is running, then:

```bash
docker compose down
```

If you also want to delete the database and start completely fresh the next time:

```bash
docker compose down -v
```
