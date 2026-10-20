from datetime import datetime, timezone

from trucktwin.diagnostics import detect_events
from trucktwin.models import OperatingMode
from trucktwin.simulator import generate_message


def test_highway_message_has_no_diagnostic_events() -> None:
    message = generate_message(mode=OperatingMode.HIGHWAY)

    assert detect_events(message) == []


def test_overheating_message_creates_event_with_evidence() -> None:
    message = generate_message(
        mode=OperatingMode.OVERHEATING,
        timestamp=datetime(2026, 10, 21, tzinfo=timezone.utc),
    )

    events = detect_events(message)

    assert len(events) == 1
    assert events[0].event_type == "ENGINE_OVERHEATING"
    assert events[0].evidence["engine_temperature_c"] == 108.3


def test_brake_pressure_is_high_severity_when_vehicle_is_moving() -> None:
    message = generate_message(mode=OperatingMode.LOW_BRAKE_PRESSURE)

    events = detect_events(message)

    assert events[0].severity == "high"
