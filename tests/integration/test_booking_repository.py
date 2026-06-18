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


def test_find_overlapping_returns_empty_for_non_overlapping_dates(booking_repo, persisted_vehicle, sample_booking):
    booking_repo.add(sample_booking)  # Jan 1–5

    result = booking_repo.find_overlapping(persisted_vehicle.id, date(2025, 1, 6), date(2025, 1, 10))

    assert result == []


def test_find_overlapping_returns_booking_when_dates_overlap(booking_repo, persisted_vehicle, sample_booking):
    booking_repo.add(sample_booking)  # Jan 1–5

    result = booking_repo.find_overlapping(persisted_vehicle.id, date(2025, 1, 3), date(2025, 1, 8))

    assert len(result) == 1
    assert result[0].id == sample_booking.id


def test_find_overlapping_returns_empty_for_adjacent_range_after(booking_repo, persisted_vehicle, sample_booking):
    booking_repo.add(sample_booking)  # Jan 1–5

    result = booking_repo.find_overlapping(persisted_vehicle.id, date(2025, 1, 5), date(2025, 1, 8))

    assert result == []


def test_find_overlapping_returns_empty_for_adjacent_range_before(booking_repo, persisted_vehicle, sample_booking):
    booking_repo.add(sample_booking)  # Jan 1–5

    result = booking_repo.find_overlapping(persisted_vehicle.id, date(2024, 12, 28), date(2025, 1, 1))

    assert result == []


def test_find_overlapping_ignores_other_vehicles(booking_repo, vehicle_repo, persisted_vehicle, sample_booking):
    booking_repo.add(sample_booking)  # booked on persisted_vehicle

    other_vehicle = Vehicle(id=uuid4(), dealer="Other", daily_price=Decimal("50.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(other_vehicle)

    result = booking_repo.find_overlapping(other_vehicle.id, date(2025, 1, 1), date(2025, 1, 5))

    assert result == []


def test_db_constraint_prevents_concurrent_overlapping_bookings(db_session, booking_repo, persisted_vehicle):
    from oscars.domain.exceptions import OverlappingBookingError

    first = Booking(
        id=uuid4(),
        vehicle_id=persisted_vehicle.id,
        start_date=date(2025, 2, 1),
        end_date=date(2025, 2, 5),
        price=Decimal("400.00"),
    )
    duplicate = Booking(
        id=uuid4(),
        vehicle_id=persisted_vehicle.id,
        start_date=date(2025, 2, 1),
        end_date=date(2025, 2, 5),
        price=Decimal("400.00"),
    )

    booking_repo.add(first)

    nested = db_session.begin_nested()
    with pytest.raises(OverlappingBookingError):
        booking_repo.add(duplicate)
    nested.rollback()
