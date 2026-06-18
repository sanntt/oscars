from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from oscars.domain.entities import Booking, Vehicle


class VehicleRepository(ABC):
    @abstractmethod
    def add(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        pass

    @abstractmethod
    def update(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    def list_all(self) -> list[Vehicle]:
        pass

    @abstractmethod
    def list_available(self, start_date: date | None, end_date: date | None) -> list[Vehicle]:
        pass


class BookingRepository(ABC):
    @abstractmethod
    def add(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def get_by_id(self, booking_id: UUID) -> Booking | None:
        pass

    @abstractmethod
    def find_overlapping(self, vehicle_id: UUID, start_date: date, end_date: date) -> list[Booking]:
        pass
