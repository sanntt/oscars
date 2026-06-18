from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class VehicleCreate(BaseModel):
    dealer: str
    daily_price: Decimal


class VehicleStatusUpdate(BaseModel):
    status: str


class VehicleResponse(BaseModel):
    id: UUID
    dealer: str
    daily_price: Decimal
    status: str
