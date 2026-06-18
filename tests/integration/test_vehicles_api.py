from decimal import Decimal
from uuid import uuid4

from oscars.domain.entities import Vehicle, VehicleStatus


def test_create_vehicle_returns_201_with_vehicle(api_client):
    response = api_client.post("/vehicles", json={"dealer": "Best Cars", "daily_price": "99.99"})

    assert response.status_code == 201
    body = response.json()
    assert body["dealer"] == "Best Cars"
    assert body["daily_price"] == "99.99"
    assert body["status"] == "available"
    assert "id" in body


def test_create_vehicle_returns_422_when_fields_are_missing(api_client):
    response = api_client.post("/vehicles", json={"dealer": "Best Cars"})

    assert response.status_code == 422


def test_list_available_returns_only_non_maintenance_vehicles(api_client, vehicle_repo):
    vehicle_repo.add(
        Vehicle(id=uuid4(), dealer="Available Co", daily_price=Decimal("50.00"), status=VehicleStatus.AVAILABLE)
    )
    vehicle_repo.add(
        Vehicle(id=uuid4(), dealer="Broken Co", daily_price=Decimal("50.00"), status=VehicleStatus.MAINTENANCE)
    )

    response = api_client.get("/vehicles")

    assert response.status_code == 200
    dealers = [v["dealer"] for v in response.json()]
    assert "Available Co" in dealers
    assert "Broken Co" not in dealers


def test_list_available_returns_empty_when_all_in_maintenance(api_client, vehicle_repo):
    vehicle_repo.add(
        Vehicle(id=uuid4(), dealer="Broken Co", daily_price=Decimal("50.00"), status=VehicleStatus.MAINTENANCE)
    )

    response = api_client.get("/vehicles")

    assert response.status_code == 200
    assert response.json() == []


def test_list_available_accepts_date_range_params(api_client):
    response = api_client.get("/vehicles?start_date=2025-01-01&end_date=2025-01-05")

    assert response.status_code == 200


def test_update_status_to_maintenance(api_client, vehicle_repo):
    vehicle = Vehicle(id=uuid4(), dealer="Fast Co", daily_price=Decimal("80.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(vehicle)

    response = api_client.patch(f"/vehicles/{vehicle.id}/status", json={"status": "maintenance"})

    assert response.status_code == 200
    assert response.json()["status"] == "maintenance"


def test_update_status_returns_404_for_unknown_vehicle(api_client):
    response = api_client.patch(f"/vehicles/{uuid4()}/status", json={"status": "maintenance"})

    assert response.status_code == 404


def test_update_status_returns_422_for_invalid_status(api_client):
    created = api_client.post("/vehicles", json={"dealer": "Fast Co", "daily_price": "80.00"})
    vehicle_id = created.json()["id"]

    response = api_client.patch(f"/vehicles/{vehicle_id}/status", json={"status": "flying"})

    assert response.status_code == 422


def test_list_available_excludes_vehicles_booked_in_requested_range(api_client, vehicle_repo):
    booked = Vehicle(id=uuid4(), dealer="Booked Co", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    free = Vehicle(id=uuid4(), dealer="Free Co", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(booked)
    vehicle_repo.add(free)

    api_client.post(
        "/bookings",
        json={"vehicle_id": str(booked.id), "start_date": "2025-06-01", "end_date": "2025-06-10"},
    )

    response = api_client.get("/vehicles?start_date=2025-06-05&end_date=2025-06-08")

    dealers = [v["dealer"] for v in response.json()]
    assert "Booked Co" not in dealers
    assert "Free Co" in dealers


def test_list_available_includes_vehicle_booked_on_different_dates(api_client, vehicle_repo):
    vehicle = Vehicle(
        id=uuid4(), dealer="Available Later", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE
    )
    vehicle_repo.add(vehicle)

    api_client.post(
        "/bookings",
        json={"vehicle_id": str(vehicle.id), "start_date": "2025-07-01", "end_date": "2025-07-05"},
    )

    response = api_client.get("/vehicles?start_date=2025-07-10&end_date=2025-07-15")

    dealers = [v["dealer"] for v in response.json()]
    assert "Available Later" in dealers


def test_list_available_without_date_range_ignores_bookings(api_client, vehicle_repo):
    vehicle = Vehicle(id=uuid4(), dealer="Always Shown", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(vehicle)

    api_client.post(
        "/bookings",
        json={"vehicle_id": str(vehicle.id), "start_date": "2025-08-01", "end_date": "2025-08-10"},
    )

    response = api_client.get("/vehicles")

    dealers = [v["dealer"] for v in response.json()]
    assert "Always Shown" in dealers
