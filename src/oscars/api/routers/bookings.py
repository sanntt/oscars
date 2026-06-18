from fastapi import APIRouter, Depends, HTTPException

from oscars.api.deps import get_booking_repository, get_vehicle_repository
from oscars.api.schemas import BookingCreate, BookingResponse
from oscars.application.bookings import create_booking
from oscars.domain.exceptions import InvalidDateRangeError, VehicleInMaintenanceError, VehicleNotFoundError
from oscars.domain.repositories import BookingRepository, VehicleRepository

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=201)
def create(
    body: BookingCreate,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
    booking_repo: BookingRepository = Depends(get_booking_repository),
):
    try:
        booking = create_booking(body.vehicle_id, body.start_date, body.end_date, vehicle_repo, booking_repo)
    except VehicleNotFoundError:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    except VehicleInMaintenanceError:
        raise HTTPException(status_code=409, detail="Vehicle is in maintenance and cannot be booked")
    except InvalidDateRangeError:
        raise HTTPException(status_code=422, detail="end_date must be after start_date")
    return BookingResponse(
        id=booking.id,
        vehicle_id=booking.vehicle_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        price=booking.price,
    )
