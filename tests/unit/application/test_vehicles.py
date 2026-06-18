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

    def update(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    def list_all(self):
        return list(self._store.values())

    def list_available(self, start_date, end_date):
        from oscars.domain.entities import VehicleStatus

        return [v for v in self._store.values() if v.status != VehicleStatus.MAINTENANCE]


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


def test_update_vehicle_updates_status_to_maintenance(repo):
    from oscars.application.vehicles import create_vehicle, update_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)
    updated = update_vehicle(vehicle.id, None, None, VehicleStatus.MAINTENANCE, repo)

    assert updated.status == VehicleStatus.MAINTENANCE


def test_update_vehicle_updates_status_back_to_available(repo):
    from oscars.application.vehicles import create_vehicle, update_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)
    update_vehicle(vehicle.id, None, None, VehicleStatus.MAINTENANCE, repo)
    updated = update_vehicle(vehicle.id, None, None, VehicleStatus.AVAILABLE, repo)

    assert updated.status == VehicleStatus.AVAILABLE


def test_update_vehicle_updates_dealer(repo):
    from oscars.application.vehicles import create_vehicle, update_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)
    updated = update_vehicle(vehicle.id, "Speed Motors", None, None, repo)

    assert updated.dealer == "Speed Motors"


def test_update_vehicle_updates_daily_price(repo):
    from oscars.application.vehicles import create_vehicle, update_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)
    updated = update_vehicle(vehicle.id, None, Decimal("200.00"), None, repo)

    assert updated.daily_price == Decimal("200.00")


def test_update_vehicle_does_not_change_unspecified_fields(repo):
    from oscars.application.vehicles import create_vehicle, update_vehicle

    vehicle = create_vehicle("Best Cars", Decimal("75.00"), repo)
    updated = update_vehicle(vehicle.id, "New Name", None, None, repo)

    assert updated.daily_price == Decimal("75.00")
    assert updated.status == VehicleStatus.AVAILABLE


def test_update_vehicle_raises_when_not_found(repo):
    from uuid import uuid4

    from oscars.application.vehicles import update_vehicle
    from oscars.domain.exceptions import VehicleNotFoundError

    with pytest.raises(VehicleNotFoundError):
        update_vehicle(uuid4(), None, None, VehicleStatus.MAINTENANCE, repo)
