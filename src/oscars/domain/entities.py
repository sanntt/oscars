import enum
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


class VehicleStatus(enum.Enum):
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"


@dataclass
class Vehicle:
    id: UUID
    dealer: str
    daily_price: Decimal
    status: VehicleStatus


@dataclass
class Booking:
    id: UUID
    vehicle_id: UUID
    start_date: date
    end_date: date
    price: Decimal
