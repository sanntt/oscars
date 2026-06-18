from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from oscars.domain.entities import Booking
from oscars.domain.repositories import BookingRepository
from oscars.infrastructure.models import BookingModel


class SqlAlchemyBookingRepository(BookingRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, booking: Booking) -> Booking:
        record = BookingModel(
            id=booking.id,
            vehicle_id=booking.vehicle_id,
            start_date=booking.start_date,
            end_date=booking.end_date,
            price=booking.price,
        )
        self._session.add(record)
        self._session.flush()
        return booking

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        record = self._session.get(BookingModel, booking_id)
        return self._to_entity(record) if record else None

    def find_overlapping(self, vehicle_id: UUID, start_date: date, end_date: date) -> list[Booking]:
        return []

    def _to_entity(self, record: BookingModel) -> Booking:
        return Booking(
            id=record.id,
            vehicle_id=record.vehicle_id,
            start_date=record.start_date,
            end_date=record.end_date,
            price=Decimal(str(record.price)),
        )
