from pathlib import Path

from fastapi.testclient import TestClient

from trucktwin.api import create_app
from trucktwin.storage import TelemetryRepository

repository = TelemetryRepository(Path("/tmp/trucktwin-test.db"))
client = TestClient(create_app(repository))


def setup_function() -> None:
    repository.clear()


def test_ingest_telemetry_and_read_diagnostic_events() -> None:
    response = client.post(
        "/telemetry",
        json={
            "vehicle_id": "truck-001",
            "timestamp": "2026-10-21T00:00:00Z",
            "software_version": "1.0.0",
            "operating_mode": "overheating",
            "signals": {
                "speed_kmh": 71,
                "engine_temperature_c": 108.3,
                "battery_voltage_v": 23.9,
                "brake_pressure_bar": 8,
            },
        },
    )

    assert response.status_code == 201
    events_response = client.get("/vehicles/truck-001/events")
    assert events_response.status_code == 200
    assert events_response.json()[0]["event_type"] == "ENGINE_OVERHEATING"


def test_unknown_vehicle_returns_not_found() -> None:
    response = client.get("/vehicles/unknown/events")

    assert response.status_code == 404


def test_extra_telemetry_fields_are_rejected() -> None:
    response = client.post(
        "/telemetry",
        json={
            "vehicle_id": "truck-001",
            "timestamp": "2026-10-21T00:00:00Z",
            "software_version": "1.0.0",
            "operating_mode": "normal",
            "signals": {
                "speed_kmh": 0,
                "engine_temperature_c": 82,
                "battery_voltage_v": 24.2,
                "brake_pressure_bar": 8.5,
                "unexpected": 1,
            },
        },
    )

    assert response.status_code == 422


def test_dashboard_is_available() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "TruckTwin AI" in response.text
    assert "Diagnostic events" in response.text
