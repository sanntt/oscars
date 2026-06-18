import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def pytest_configure(config):
    if not os.environ.get("DATABASE_URL"):
        return

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def db_engine():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set — skipping integration tests")
    return create_engine(database_url)


@pytest.fixture(scope="session")
def db_connection(db_engine):
    with db_engine.connect() as connection:
        yield connection


@pytest.fixture
def db_session(db_connection):
    db_connection.execute(text("BEGIN"))
    Session = sessionmaker(bind=db_connection)
    session = Session()
    yield session
    session.close()
    db_connection.execute(text("ROLLBACK"))


@pytest.fixture
def vehicle_repo(db_session):
    from oscars.infrastructure.vehicle_repository import SqlAlchemyVehicleRepository

    return SqlAlchemyVehicleRepository(db_session)


@pytest.fixture
def booking_repo(db_session):
    from oscars.infrastructure.booking_repository import SqlAlchemyBookingRepository

    return SqlAlchemyBookingRepository(db_session)


@pytest.fixture
def api_client(db_session):
    from fastapi.testclient import TestClient

    from oscars.api.deps import get_booking_repository, get_vehicle_repository
    from oscars.api.main import create_app
    from oscars.infrastructure.booking_repository import SqlAlchemyBookingRepository
    from oscars.infrastructure.database import get_db
    from oscars.infrastructure.vehicle_repository import SqlAlchemyVehicleRepository

    application = create_app()
    application.dependency_overrides[get_db] = lambda: db_session
    application.dependency_overrides[get_vehicle_repository] = lambda: SqlAlchemyVehicleRepository(db_session)
    application.dependency_overrides[get_booking_repository] = lambda: SqlAlchemyBookingRepository(db_session)

    with TestClient(application) as client:
        yield client
