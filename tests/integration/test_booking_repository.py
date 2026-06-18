from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from oscars.domain.entities import Booking, Vehicle, VehicleStatus


@pytest.fixture
def persisted_vehicle(vehicle_repo):
    vehicle = Vehicle(id=uuid4(), dealer="Best Cars", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(vehicle)
    return vehicle


@pytest.fixture
def sample_booking(persisted_vehicle):
    return Booking(
        id=uuid4(),
        vehicle_id=persisted_vehicle.id,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 5),
        price=Decimal("400.00"),
    )


def test_add_persists_booking(booking_repo, sample_booking):
    booking_repo.add(sample_booking)

    found = booking_repo.get_by_id(sample_booking.id)

    assert found is not None
    assert found.id == sample_booking.id
    assert found.vehicle_id == sample_booking.vehicle_id
    assert found.start_date == sample_booking.start_date
    assert found.end_date == sample_booking.end_date
    assert found.price == sample_booking.price


def test_get_by_id_returns_none_for_unknown_id(booking_repo):
    result = booking_repo.get_by_id(uuid4())

    assert result is None
