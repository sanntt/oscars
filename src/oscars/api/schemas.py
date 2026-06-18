from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from oscars.domain.entities import VehicleStatus


class VehicleCreate(BaseModel):
    dealer: str = Field(min_length=1)
    daily_price: Decimal = Field(gt=0, lt=10000)


class VehicleStatusUpdate(BaseModel):
    status: VehicleStatus


class VehicleResponse(BaseModel):
    id: UUID
    dealer: str
    daily_price: Decimal
    status: str


class BookingCreate(BaseModel):
    vehicle_id: UUID
    start_date: date
    end_date: date


class BookingResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    start_date: date
    end_date: date
    price: Decimal
