from fastapi import Depends
from sqlalchemy.orm import Session

from oscars.domain.repositories import BookingRepository, VehicleRepository
from oscars.infrastructure.booking_repository import SqlAlchemyBookingRepository
from oscars.infrastructure.database import get_db
from oscars.infrastructure.vehicle_repository import SqlAlchemyVehicleRepository


def get_vehicle_repository(db: Session = Depends(get_db)) -> VehicleRepository:
    return SqlAlchemyVehicleRepository(db)


def get_booking_repository(db: Session = Depends(get_db)) -> BookingRepository:
    return SqlAlchemyBookingRepository(db)
