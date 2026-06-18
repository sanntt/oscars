from decimal import Decimal
from uuid import UUID

import pytest

from oscars.domain.entities import Vehicle, VehicleStatus
from oscars.domain.repositories import VehicleRepository


class InMemoryVehicleRepository(VehicleRepository):
    def __init__(self):
        self._store: dict = {}

    def add(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    def get_by_id(self, vehicle_id):
        return self._store.get(vehicle_id)

    def list_all(self):
        return list(self._store.values())


@pytest.fixture
def repo():
    return InMemoryVehicleRepository()


def test_create_vehicle_returns_available_vehicle(repo):
    from oscars.application.vehicles import create_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)

    assert vehicle.status == VehicleStatus.AVAILABLE


def test_create_vehicle_returns_vehicle_with_uuid(repo):
    from oscars.application.vehicles import create_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)

    assert isinstance(vehicle.id, UUID)


def test_create_vehicle_persists_to_repository(repo):
    from oscars.application.vehicles import create_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)

    assert repo.get_by_id(vehicle.id) is not None


def test_create_vehicle_stores_correct_dealer_and_price(repo):
    from oscars.application.vehicles import create_vehicle

    vehicle = create_vehicle("Speed Motors", Decimal("120.50"), repo)

    assert vehicle.dealer == "Speed Motors"
    assert vehicle.daily_price == Decimal("120.50")
