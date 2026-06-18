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
