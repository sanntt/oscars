from decimal import Decimal
from uuid import uuid4

import pytest

from oscars.domain.entities import Vehicle, VehicleStatus


@pytest.fixture
def available_vehicle(vehicle_repo):
    vehicle = Vehicle(id=uuid4(), dealer="Best Cars", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(vehicle)
    return vehicle


@pytest.fixture
def maintenance_vehicle(vehicle_repo):
    vehicle = Vehicle(id=uuid4(), dealer="Broken Co", daily_price=Decimal("100.00"), status=VehicleStatus.MAINTENANCE)
    vehicle_repo.add(vehicle)
    return vehicle


def test_create_booking_returns_201_with_booking(api_client, available_vehicle):
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-01-01", "end_date": "2025-01-05"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["vehicle_id"] == str(available_vehicle.id)
    assert body["start_date"] == "2025-01-01"
    assert body["end_date"] == "2025-01-05"
    assert body["price"] == "400.00"
    assert "id" in body


def test_create_booking_returns_404_for_unknown_vehicle(api_client):
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(uuid4()), "start_date": "2025-01-01", "end_date": "2025-01-05"},
    )

    assert response.status_code == 404


def test_create_booking_returns_409_when_vehicle_in_maintenance(api_client, maintenance_vehicle):
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(maintenance_vehicle.id), "start_date": "2025-01-01", "end_date": "2025-01-05"},
    )

    assert response.status_code == 409


def test_create_booking_returns_422_when_start_date_equals_end_date(api_client, available_vehicle):
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-01-05", "end_date": "2025-01-05"},
    )

    assert response.status_code == 422


def test_create_booking_returns_422_when_start_date_is_after_end_date(api_client, available_vehicle):
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-01-10", "end_date": "2025-01-05"},
    )

    assert response.status_code == 422


def test_create_booking_returns_422_when_fields_are_missing(api_client):
    response = api_client.post("/bookings", json={"vehicle_id": str(uuid4())})

    assert response.status_code == 422


def test_create_booking_returns_409_when_dates_overlap(api_client, available_vehicle):
    api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-03-01", "end_date": "2025-03-10"},
    )

    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-03-05", "end_date": "2025-03-15"},
    )

    assert response.status_code == 409


def test_create_booking_allows_adjacent_bookings_on_same_vehicle(api_client, available_vehicle):
    api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-04-01", "end_date": "2025-04-05"},
    )

    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(available_vehicle.id), "start_date": "2025-04-05", "end_date": "2025-04-10"},
    )

    assert response.status_code == 201


def test_create_booking_returns_422_when_duration_exceeds_365_days(api_client, available_vehicle):
    response = api_client.post(
        "/bookings",
        json={
            "vehicle_id": str(available_vehicle.id),
            "start_date": "2025-01-01",
            "end_date": "2026-01-02",
        },
    )

    assert response.status_code == 422


def test_create_booking_allows_booking_of_exactly_365_days(api_client, available_vehicle):
    response = api_client.post(
        "/bookings",
        json={
            "vehicle_id": str(available_vehicle.id),
            "start_date": "2025-01-01",
            "end_date": "2026-01-01",
        },
    )

    assert response.status_code == 201


def test_create_booking_allows_same_dates_on_different_vehicles(api_client, vehicle_repo):
    vehicle_a = Vehicle(id=uuid4(), dealer="A", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_b = Vehicle(id=uuid4(), dealer="B", daily_price=Decimal("100.00"), status=VehicleStatus.AVAILABLE)
    vehicle_repo.add(vehicle_a)
    vehicle_repo.add(vehicle_b)

    api_client.post(
        "/bookings",
        json={"vehicle_id": str(vehicle_a.id), "start_date": "2025-05-01", "end_date": "2025-05-05"},
    )
    response = api_client.post(
        "/bookings",
        json={"vehicle_id": str(vehicle_b.id), "start_date": "2025-05-01", "end_date": "2025-05-05"},
    )

    assert response.status_code == 201
