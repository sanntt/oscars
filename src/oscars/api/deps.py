from fastapi import Depends
from sqlalchemy.orm import Session

from oscars.domain.repositories import VehicleRepository
from oscars.infrastructure.database import get_db
from oscars.infrastructure.vehicle_repository import SqlAlchemyVehicleRepository


def get_vehicle_repository(db: Session = Depends(get_db)) -> VehicleRepository:
    return SqlAlchemyVehicleRepository(db)
