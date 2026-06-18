from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from oscars.api.deps import get_vehicle_repository
from oscars.api.schemas import VehicleCreate, VehicleResponse, VehicleStatusUpdate
from oscars.application.vehicles import create_vehicle, update_vehicle_status
from oscars.domain.exceptions import VehicleNotFoundError
from oscars.domain.repositories import VehicleRepository

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleResponse, status_code=201)
def create(body: VehicleCreate, repo: VehicleRepository = Depends(get_vehicle_repository)):
    vehicle = create_vehicle(body.dealer, body.daily_price, repo)
    return VehicleResponse(
        id=vehicle.id, dealer=vehicle.dealer, daily_price=vehicle.daily_price, status=vehicle.status.value
    )


@router.get("", response_model=list[VehicleResponse])
def list_available(
    start_date: date | None = None,
    end_date: date | None = None,
    repo: VehicleRepository = Depends(get_vehicle_repository),
):
    if (start_date is None) != (end_date is None):
        raise HTTPException(status_code=422, detail="Provide both start_date and end_date, or neither")
    if start_date is not None and start_date >= end_date:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")
    vehicles = repo.list_available(start_date, end_date)
    return [
        VehicleResponse(id=v.id, dealer=v.dealer, daily_price=v.daily_price, status=v.status.value) for v in vehicles
    ]


@router.patch("/{vehicle_id}/status", response_model=VehicleResponse)
def update_status(
    vehicle_id: UUID,
    body: VehicleStatusUpdate,
    repo: VehicleRepository = Depends(get_vehicle_repository),
):
    try:
        vehicle = update_vehicle_status(vehicle_id, body.status, repo)
    except VehicleNotFoundError:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return VehicleResponse(
        id=vehicle.id, dealer=vehicle.dealer, daily_price=vehicle.daily_price, status=vehicle.status.value
    )
