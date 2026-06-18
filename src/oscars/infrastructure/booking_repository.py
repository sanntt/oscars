from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from oscars.domain.entities import Booking
from oscars.domain.exceptions import OverlappingBookingError
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
        try:
            self._session.flush()
        except IntegrityError as exc:
            if "overlapping_bookings_excl" in str(exc.orig):
                raise OverlappingBookingError(booking.vehicle_id)
            raise
        return booking

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        record = self._session.get(BookingModel, booking_id)
        return self._to_entity(record) if record else None

    def find_overlapping(self, vehicle_id: UUID, start_date: date, end_date: date) -> list[Booking]:
        records = (
            self._session.query(BookingModel)
            .filter(
                BookingModel.vehicle_id == vehicle_id,
                BookingModel.start_date < end_date,
                BookingModel.end_date > start_date,
            )
            .all()
        )
        return [self._to_entity(r) for r in records]

    def _to_entity(self, record: BookingModel) -> Booking:
        return Booking(
            id=record.id,
            vehicle_id=record.vehicle_id,
            start_date=record.start_date,
            end_date=record.end_date,
            price=Decimal(str(record.price)),
        )
