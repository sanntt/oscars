from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

from oscars.domain.entities import VehicleStatus

_Dealer = Annotated[str, Field(min_length=1)]
_DailyPrice = Annotated[Decimal, Field(gt=0, lt=10000)]


class VehicleCreate(BaseModel):
    dealer: _Dealer
    daily_price: _DailyPrice


class VehicleUpdate(BaseModel):
    dealer: _Dealer | None = None
    daily_price: _DailyPrice | None = None
    status: VehicleStatus | None = None


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
