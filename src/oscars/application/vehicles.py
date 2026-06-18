from decimal import Decimal
from uuid import UUID, uuid4

from oscars.domain.entities import Vehicle, VehicleStatus
from oscars.domain.exceptions import VehicleNotFoundError
from oscars.domain.repositories import VehicleRepository


def create_vehicle(dealer: str, daily_price: Decimal, repo: VehicleRepository) -> Vehicle:
    vehicle = Vehicle(
        id=uuid4(),
        dealer=dealer,
        daily_price=daily_price,
        status=VehicleStatus.AVAILABLE,
    )
    return repo.add(vehicle)


def update_vehicle(
    vehicle_id: UUID,
    dealer: str | None,
    daily_price: Decimal | None,
    new_status: VehicleStatus | None,
    repo: VehicleRepository,
) -> Vehicle:
    vehicle = repo.get_by_id(vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    if dealer is not None:
        vehicle.dealer = dealer
    if daily_price is not None:
        vehicle.daily_price = daily_price
    if new_status is not None:
        vehicle.status = new_status
    return repo.update(vehicle)
