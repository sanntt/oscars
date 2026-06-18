from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from oscars.domain.entities import Booking, Vehicle, VehicleStatus
from oscars.domain.exceptions import (
    InvalidDateRangeError,
    OverlappingBookingError,
    VehicleInMaintenanceError,
    VehicleNotFoundError,
)
from oscars.domain.repositories import BookingRepository, VehicleRepository


class InMemoryVehicleRepository(VehicleRepository):
    def __init__(self, vehicles: list[Vehicle] = None):
        self._store = {v.id: v for v in (vehicles or [])}

    def add(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return self._store.get(vehicle_id)

    def update(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    def list_all(self) -> list[Vehicle]:
        return list(self._store.values())

    def list_available(self, start_date, end_date) -> list[Vehicle]:
        return [v for v in self._store.values() if v.status != VehicleStatus.MAINTENANCE]


class InMemoryBookingRepository(BookingRepository):
    def __init__(self):
        self._store: dict = {}

    def add(self, booking: Booking) -> Booking:
        self._store[booking.id] = booking
        return booking

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        return self._store.get(booking_id)

    def find_overlapping(self, vehicle_id: UUID, start_date: date, end_date: date) -> list[Booking]:
        return [
            b
            for b in self._store.values()
            if b.vehicle_id == vehicle_id and b.start_date < end_date and b.end_date > start_date
        ]


@pytest.fixture
def available_vehicle():
    return Vehicle(id=uuid4(), dealer="Best Cars", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)


@pytest.fixture
def maintenance_vehicle():
    return Vehicle(id=uuid4(), dealer="Broken Co", daily_price=Decimal("100.00"), status=VehicleStatus.MAINTENANCE)


def test_create_booking_returns_booking_with_uuid(available_vehicle):
    from oscars.application.bookings import create_booking

    booking = create_booking(
        available_vehicle.id,
        date(2025, 1, 1),
        date(2025, 1, 5),
        InMemoryVehicleRepository([available_vehicle]),
        InMemoryBookingRepository(),
    )

    assert isinstance(booking.id, UUID)


def test_create_booking_calculates_price_from_daily_rate(available_vehicle):
    from oscars.application.bookings import create_booking

    booking = create_booking(
        available_vehicle.id,
        date(2025, 1, 1),
        date(2025, 1, 5),
        InMemoryVehicleRepository([available_vehicle]),
        InMemoryBookingRepository(),
    )

    assert booking.price == Decimal("400.00")


def test_create_booking_price_reflects_number_of_days(available_vehicle):
    from oscars.application.bookings import create_booking

    booking = create_booking(
        available_vehicle.id,
        date(2025, 6, 1),
        date(2025, 6, 11),
        InMemoryVehicleRepository([available_vehicle]),
        InMemoryBookingRepository(),
    )

    assert booking.price == Decimal("1000.00")


def test_create_booking_raises_when_start_date_equals_end_date(available_vehicle):
    from oscars.application.bookings import create_booking

    with pytest.raises(InvalidDateRangeError):
        create_booking(
            available_vehicle.id,
            date(2025, 1, 5),
            date(2025, 1, 5),
            InMemoryVehicleRepository([available_vehicle]),
            InMemoryBookingRepository(),
        )


def test_create_booking_raises_when_start_date_is_after_end_date(available_vehicle):
    from oscars.application.bookings import create_booking

    with pytest.raises(InvalidDateRangeError):
        create_booking(
            available_vehicle.id,
            date(2025, 1, 10),
            date(2025, 1, 5),
            InMemoryVehicleRepository([available_vehicle]),
            InMemoryBookingRepository(),
        )


def test_create_booking_raises_when_vehicle_not_found():
    from oscars.application.bookings import create_booking

    with pytest.raises(VehicleNotFoundError):
        create_booking(
            uuid4(),
            date(2025, 1, 1),
            date(2025, 1, 5),
            InMemoryVehicleRepository(),
            InMemoryBookingRepository(),
        )


def test_create_booking_raises_when_vehicle_is_in_maintenance(maintenance_vehicle):
    from oscars.application.bookings import create_booking

    with pytest.raises(VehicleInMaintenanceError):
        create_booking(
            maintenance_vehicle.id,
            date(2025, 1, 1),
            date(2025, 1, 5),
            InMemoryVehicleRepository([maintenance_vehicle]),
            InMemoryBookingRepository(),
        )


def test_create_booking_persists_to_repository(available_vehicle):
    from oscars.application.bookings import create_booking

    booking_repo = InMemoryBookingRepository()
    booking = create_booking(
        available_vehicle.id,
        date(2025, 1, 1),
        date(2025, 1, 5),
        InMemoryVehicleRepository([available_vehicle]),
        booking_repo,
    )

    assert booking_repo.get_by_id(booking.id) is not None


# --- Overlap cases ---
# All use half-open intervals [start, end). A booking Jan 1–5 occupies Jan 1, 2, 3, 4.


def _book(vehicle, booking_repo, start, end):
    from oscars.application.bookings import create_booking

    return create_booking(
        vehicle.id,
        start,
        end,
        InMemoryVehicleRepository([vehicle]),
        booking_repo,
    )


def test_overlap_raises_when_new_booking_starts_inside_existing(available_vehicle):
    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 5))

    with pytest.raises(OverlappingBookingError):
        _book(available_vehicle, booking_repo, date(2025, 1, 3), date(2025, 1, 8))


def test_overlap_raises_when_new_booking_ends_inside_existing(available_vehicle):
    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 5), date(2025, 1, 10))

    with pytest.raises(OverlappingBookingError):
        _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 7))


def test_overlap_raises_when_new_booking_is_identical(available_vehicle):
    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 5))

    with pytest.raises(OverlappingBookingError):
        _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 5))


def test_overlap_raises_when_new_booking_contains_existing(available_vehicle):
    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 3), date(2025, 1, 4))

    with pytest.raises(OverlappingBookingError):
        _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 10))


def test_no_overlap_when_new_booking_starts_on_existing_end_date(available_vehicle):

    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 5))

    booking = _book(available_vehicle, booking_repo, date(2025, 1, 5), date(2025, 1, 8))

    assert booking is not None


def test_no_overlap_when_new_booking_ends_on_existing_start_date(available_vehicle):
    booking_repo = InMemoryBookingRepository()
    _book(available_vehicle, booking_repo, date(2025, 1, 5), date(2025, 1, 8))

    booking = _book(available_vehicle, booking_repo, date(2025, 1, 1), date(2025, 1, 5))

    assert booking is not None


def test_no_overlap_for_different_vehicles():
    vehicle_a = Vehicle(id=uuid4(), dealer="A", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_b = Vehicle(id=uuid4(), dealer="B", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    booking_repo = InMemoryBookingRepository()

    from oscars.application.bookings import create_booking

    create_booking(
        vehicle_a.id, date(2025, 1, 1), date(2025, 1, 5), InMemoryVehicleRepository([vehicle_a]), booking_repo
    )
    booking = create_booking(
        vehicle_b.id, date(2025, 1, 1), date(2025, 1, 5), InMemoryVehicleRepository([vehicle_b]), booking_repo
    )

    assert booking is not None
