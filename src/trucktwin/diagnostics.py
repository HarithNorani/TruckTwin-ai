from collections.abc import Iterable

from .models import DiagnosticEvent, Severity, TelemetryMessage


def detect_events(message: TelemetryMessage) -> list[DiagnosticEvent]:
    """Return deterministic investigation events for a telemetry message."""
    signals = message.signals
    checks: list[tuple[bool, str, Severity, str, dict[str, float]]] = [
        (
            signals.engine_temperature_c > 105,
            "ENGINE_OVERHEATING",
            Severity.MEDIUM,
            "Engine temperature exceeded the engineering warning threshold.",
            {"engine_temperature_c": signals.engine_temperature_c},
        ),
        (
            signals.speed_kmh > 30 and signals.brake_pressure_bar < 6,
            "LOW_BRAKE_PRESSURE",
            Severity.HIGH,
            "Brake pressure is below the threshold while the vehicle is moving.",
            {
                "speed_kmh": signals.speed_kmh,
                "brake_pressure_bar": signals.brake_pressure_bar,
            },
        ),
        (
            signals.battery_voltage_v < 22,
            "LOW_BATTERY_VOLTAGE",
            Severity.MEDIUM,
            "Battery voltage fell below the engineering warning threshold.",
            {"battery_voltage_v": signals.battery_voltage_v},
        ),
    ]

    return [
        DiagnosticEvent(
            event_id=f"{message.vehicle_id}-{message.timestamp.timestamp()}-{event_type}",
            vehicle_id=message.vehicle_id,
            timestamp=message.timestamp,
            event_type=event_type,
            severity=severity,
            message=event_message,
            evidence=evidence,
            software_version=message.software_version,
        )
        for condition, event_type, severity, event_message, evidence in checks
        if condition
    ]


def detect_events_from_messages(
    messages: Iterable[TelemetryMessage],
) -> list[DiagnosticEvent]:
    """Detect events across a sequence while preserving input order."""
    return [event for message in messages for event in detect_events(message)]
