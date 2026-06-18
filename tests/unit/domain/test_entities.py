from decimal import Decimal
from uuid import UUID, uuid4

from oscars.domain.entities import Vehicle, VehicleStatus


def test_vehicle_can_be_instantiated():
    vehicle = Vehicle(
        id=uuid4(),
        dealer="Best Cars",
        daily_price=Decimal("99.99"),
        status=VehicleStatus.AVAILABLE,
    )

    assert vehicle.dealer == "Best Cars"
    assert vehicle.daily_price == Decimal("99.99")
    assert vehicle.status == VehicleStatus.AVAILABLE


def test_vehicle_id_is_a_uuid():
    vehicle_id = uuid4()
    vehicle = Vehicle(id=vehicle_id, dealer="X", daily_price=Decimal("1.00"), status=VehicleStatus.AVAILABLE)

    assert isinstance(vehicle.id, UUID)
    assert vehicle.id == vehicle_id


def test_vehicle_daily_price_is_decimal():
    vehicle = Vehicle(id=uuid4(), dealer="X", daily_price=Decimal("50.00"), status=VehicleStatus.AVAILABLE)

    assert isinstance(vehicle.daily_price, Decimal)


def test_vehicle_status_has_available_and_maintenance():
    statuses = {s.value for s in VehicleStatus}

    assert statuses == {"available", "maintenance"}
