from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from oscars.domain.entities import Booking, VehicleStatus
from oscars.domain.exceptions import (
    InvalidDateRangeError,
    OverlappingBookingError,
    VehicleInMaintenanceError,
    VehicleNotFoundError,
)
from oscars.domain.repositories import BookingRepository, VehicleRepository


def create_booking(
    vehicle_id: UUID,
    start_date: date,
    end_date: date,
    vehicle_repo: VehicleRepository,
    booking_repo: BookingRepository,
) -> Booking:
    if start_date >= end_date:
        raise InvalidDateRangeError("end_date must be after start_date")

    if (end_date - start_date).days > 365:
        raise InvalidDateRangeError("Booking duration cannot exceed 365 days")

    vehicle = vehicle_repo.get_by_id(vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)

    if vehicle.status == VehicleStatus.MAINTENANCE:
        raise VehicleInMaintenanceError(vehicle_id)

    if booking_repo.find_overlapping(vehicle_id, start_date, end_date):
        raise OverlappingBookingError(vehicle_id)

    price = vehicle.daily_price * Decimal((end_date - start_date).days)

    booking = Booking(id=uuid4(), vehicle_id=vehicle_id, start_date=start_date, end_date=end_date, price=price)
    return booking_repo.add(booking)
