import os
import pytest


def pytest_configure(config):
    if not os.environ.get("DATABASE_URL"):
        return

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
