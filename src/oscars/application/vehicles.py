from decimal import Decimal
from uuid import uuid4

from oscars.domain.entities import Vehicle, VehicleStatus
from oscars.domain.repositories import VehicleRepository


def create_vehicle(dealer: str, daily_price: Decimal, repo: VehicleRepository) -> Vehicle:
    vehicle = Vehicle(
        id=uuid4(),
        dealer=dealer,
        daily_price=daily_price,
        status=VehicleStatus.AVAILABLE,
    )
    return repo.add(vehicle)
