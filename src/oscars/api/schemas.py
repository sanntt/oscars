from datetime import date
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
