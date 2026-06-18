from decimal import Decimal
from uuid import uuid4

import pytest

from oscars.domain.entities import Vehicle, VehicleStatus


@pytest.fixture
def sample_vehicle():
    return Vehicle(
        id=uuid4(),
        dealer="Best Cars",
        daily_price=Decimal("99.99"),
        status=VehicleStatus.AVAILABLE,
    )


def test_add_persists_vehicle(vehicle_repo, sample_vehicle):
    vehicle_repo.add(sample_vehicle)

    found = vehicle_repo.get_by_id(sample_vehicle.id)

    assert found is not None
    assert found.id == sample_vehicle.id
    assert found.dealer == sample_vehicle.dealer
    assert found.daily_price == sample_vehicle.daily_price
    assert found.status == sample_vehicle.status


def test_get_by_id_returns_none_for_unknown_id(vehicle_repo):
    result = vehicle_repo.get_by_id(uuid4())

    assert result is None


def test_list_all_returns_empty_when_no_vehicles(vehicle_repo):
    result = vehicle_repo.list_all()

    assert result == []


def test_update_persists_status_change(vehicle_repo, sample_vehicle):
    vehicle_repo.add(sample_vehicle)
    sample_vehicle.status = VehicleStatus.MAINTENANCE

    vehicle_repo.update(sample_vehicle)

    found = vehicle_repo.get_by_id(sample_vehicle.id)
    assert found.status == VehicleStatus.MAINTENANCE


def test_update_reflects_new_status_on_subsequent_reads(vehicle_repo, sample_vehicle):
    vehicle_repo.add(sample_vehicle)
    sample_vehicle.status = VehicleStatus.MAINTENANCE
    vehicle_repo.update(sample_vehicle)

    sample_vehicle.status = VehicleStatus.AVAILABLE
    vehicle_repo.update(sample_vehicle)

    found = vehicle_repo.get_by_id(sample_vehicle.id)
    assert found.status == VehicleStatus.AVAILABLE


def test_list_all_returns_all_added_vehicles(vehicle_repo):
    vehicle_a = Vehicle(id=uuid4(), dealer="A", daily_price=Decimal("10.00"), status=VehicleStatus.AVAILABLE)
    vehicle_b = Vehicle(id=uuid4(), dealer="B", daily_price=Decimal("20.00"), status=VehicleStatus.MAINTENANCE)

    vehicle_repo.add(vehicle_a)
    vehicle_repo.add(vehicle_b)

    all_vehicles = vehicle_repo.list_all()

    assert len(all_vehicles) == 2
    ids = {v.id for v in all_vehicles}
    assert vehicle_a.id in ids
    assert vehicle_b.id in ids
