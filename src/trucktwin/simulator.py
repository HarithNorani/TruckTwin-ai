import argparse
import json
from datetime import datetime, timezone
from typing import Optional

from .models import OperatingMode, TelemetryMessage, TelemetrySignals


def generate_message(
    vehicle_id: str = "truck-001",
    mode: OperatingMode = OperatingMode.HIGHWAY,
    *,
    timestamp: Optional[datetime] = None,
    software_version: str = "1.0.0",
) -> TelemetryMessage:
    """Generate one deterministic synthetic telemetry message."""
    signals_by_mode = {
        OperatingMode.NORMAL: TelemetrySignals(
            speed_kmh=0, engine_temperature_c=82, battery_voltage_v=24.2, brake_pressure_bar=8.5
        ),
        OperatingMode.HIGHWAY: TelemetrySignals(
            speed_kmh=72.4, engine_temperature_c=94.5, battery_voltage_v=24.1, brake_pressure_bar=8.1
        ),
        OperatingMode.OVERHEATING: TelemetrySignals(
            speed_kmh=71, engine_temperature_c=108.3, battery_voltage_v=23.9, brake_pressure_bar=8.0
        ),
        OperatingMode.LOW_BRAKE_PRESSURE: TelemetrySignals(
            speed_kmh=65, engine_temperature_c=93, battery_voltage_v=24.0, brake_pressure_bar=4.2
        ),
        OperatingMode.LOW_BATTERY: TelemetrySignals(
            speed_kmh=45, engine_temperature_c=91, battery_voltage_v=21.4, brake_pressure_bar=8.0
        ),
    }
    return TelemetryMessage(
        vehicle_id=vehicle_id,
        timestamp=timestamp or datetime.now(timezone.utc),
        software_version=software_version,
        operating_mode=mode,
        signals=signals_by_mode[mode],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic TruckTwin telemetry.")
    parser.add_argument("--vehicle-id", default="truck-001")
    parser.add_argument("--mode", choices=[mode.value for mode in OperatingMode], default="highway")
    args = parser.parse_args()
    message = generate_message(args.vehicle_id, OperatingMode(args.mode))
    print(json.dumps(message.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
