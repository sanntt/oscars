import enum
from dataclasses import dataclass
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
