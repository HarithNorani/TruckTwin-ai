from datetime import datetime, timezone

from trucktwin.diagnostics import detect_events
from trucktwin.simulator import generate_message
from trucktwin.storage import TelemetryRepository


def test_repository_round_trips_telemetry_and_events(tmp_path) -> None:
    repository = TelemetryRepository(tmp_path / "telemetry.db")
    message = generate_message(
        vehicle_id="truck-007",
        mode="overheating",
        timestamp=datetime(2026, 10, 21, tzinfo=timezone.utc),
    )

    repository.save_telemetry(message, detect_events(message))

    assert repository.list_vehicles() == ["truck-007"]
    assert repository.telemetry_for("truck-007") == [message]
    assert repository.events_for("truck-007")[0].event_type == "ENGINE_OVERHEATING"


def test_repository_data_is_available_from_new_instance(tmp_path) -> None:
    database_path = tmp_path / "telemetry.db"
    message = generate_message(vehicle_id="truck-008")
    TelemetryRepository(database_path).save_telemetry(message, [])

    reopened = TelemetryRepository(database_path)

    assert reopened.telemetry_for("truck-008") == [message]
