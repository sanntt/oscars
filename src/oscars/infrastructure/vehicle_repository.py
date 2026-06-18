from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import exists, not_
from sqlalchemy.orm import Session

from oscars.domain.entities import Vehicle, VehicleStatus
from oscars.domain.repositories import VehicleRepository
from oscars.infrastructure.models import BookingModel, VehicleModel


class SqlAlchemyVehicleRepository(VehicleRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, vehicle: Vehicle) -> Vehicle:
        record = VehicleModel(
            id=vehicle.id,
            dealer=vehicle.dealer,
            daily_price=vehicle.daily_price,
            status=vehicle.status.value,
        )
        self._session.add(record)
        self._session.flush()
        return vehicle

    def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        record = self._session.get(VehicleModel, vehicle_id)
        return self._to_entity(record) if record else None

    def update(self, vehicle: Vehicle) -> Vehicle:
        record = self._session.get(VehicleModel, vehicle.id)
        record.status = vehicle.status.value
        self._session.flush()
        return vehicle

    def list_all(self) -> list[Vehicle]:
        records = self._session.query(VehicleModel).all()
        return [self._to_entity(r) for r in records]

    def list_available(self, start_date: date | None, end_date: date | None) -> list[Vehicle]:
        query = self._session.query(VehicleModel).filter(VehicleModel.status != VehicleStatus.MAINTENANCE.value)

        if start_date and end_date:
            booked = exists().where(
                BookingModel.vehicle_id == VehicleModel.id,
                BookingModel.start_date < end_date,
                BookingModel.end_date > start_date,
            )
            query = query.filter(not_(booked))

        return [self._to_entity(r) for r in query.all()]

    def _to_entity(self, record: VehicleModel) -> Vehicle:
        return Vehicle(
            id=record.id,
            dealer=record.dealer,
            daily_price=Decimal(str(record.daily_price)),
            status=VehicleStatus(record.status),
        )
