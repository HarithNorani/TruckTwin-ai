from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OperatingMode(str, Enum):
    NORMAL = "normal"
    HIGHWAY = "highway"
    OVERHEATING = "overheating"
    LOW_BRAKE_PRESSURE = "low_brake_pressure"
    LOW_BATTERY = "low_battery"


class TelemetrySignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speed_kmh: float = Field(ge=0, le=150)
    engine_temperature_c: float = Field(ge=-50, le=200)
    battery_voltage_v: float = Field(ge=0, le=60)
    brake_pressure_bar: float = Field(ge=0, le=20)


class TelemetryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_id: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    timestamp: datetime
    software_version: str = Field(min_length=1, max_length=32)
    operating_mode: OperatingMode
    signals: TelemetrySignals


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DiagnosticEvent(BaseModel):
    event_id: str
    vehicle_id: str
    timestamp: datetime
    event_type: str
    severity: Severity
    message: str
    evidence: dict[str, float]
    software_version: str
