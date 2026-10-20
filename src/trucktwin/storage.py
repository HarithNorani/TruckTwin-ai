import json
import sqlite3
from pathlib import Path
from typing import Optional

from .models import DiagnosticEvent, TelemetryMessage


class TelemetryRepository:
    """SQLite repository for telemetry and derived diagnostic events."""

    def __init__(self, database_path: str) -> None:
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    software_version TEXT NOT NULL,
                    operating_mode TEXT NOT NULL,
                    signals_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_timestamp
                    ON telemetry(vehicle_id, timestamp);
                CREATE TABLE IF NOT EXISTS diagnostic_events (
                    event_id TEXT PRIMARY KEY,
                    vehicle_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    software_version TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_events_vehicle_timestamp
                    ON diagnostic_events(vehicle_id, timestamp);
                """
            )

    def save_telemetry(
        self,
        message: TelemetryMessage,
        events: list[DiagnosticEvent],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO telemetry (
                    vehicle_id, timestamp, software_version, operating_mode, signals_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    message.vehicle_id,
                    message.timestamp.isoformat(),
                    message.software_version,
                    message.operating_mode.value,
                    json.dumps(message.signals.model_dump()),
                ),
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO diagnostic_events (
                    event_id, vehicle_id, timestamp, event_type, severity,
                    message, evidence_json, software_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        event.event_id,
                        event.vehicle_id,
                        event.timestamp.isoformat(),
                        event.event_type,
                        event.severity.value,
                        event.message,
                        json.dumps(event.evidence),
                        event.software_version,
                    )
                    for event in events
                ],
            )

    def list_vehicles(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT vehicle_id FROM telemetry ORDER BY vehicle_id"
            ).fetchall()
        return [row["vehicle_id"] for row in rows]

    def telemetry_for(self, vehicle_id: str) -> list[TelemetryMessage]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT vehicle_id, timestamp, software_version, operating_mode, signals_json
                FROM telemetry WHERE vehicle_id = ? ORDER BY timestamp, id
                """,
                (vehicle_id,),
            ).fetchall()
        return [
            TelemetryMessage(
                vehicle_id=row["vehicle_id"],
                timestamp=row["timestamp"],
                software_version=row["software_version"],
                operating_mode=row["operating_mode"],
                signals=json.loads(row["signals_json"]),
            )
            for row in rows
        ]

    def events_for(self, vehicle_id: str) -> list[DiagnosticEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, vehicle_id, timestamp, event_type, severity,
                       message, evidence_json, software_version
                FROM diagnostic_events WHERE vehicle_id = ? ORDER BY timestamp, event_id
                """,
                (vehicle_id,),
            ).fetchall()
        return [
            DiagnosticEvent(
                event_id=row["event_id"],
                vehicle_id=row["vehicle_id"],
                timestamp=row["timestamp"],
                event_type=row["event_type"],
                severity=row["severity"],
                message=row["message"],
                evidence=json.loads(row["evidence_json"]),
                software_version=row["software_version"],
            )
            for row in rows
        ]

    def has_vehicle(self, vehicle_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM telemetry WHERE vehicle_id = ? LIMIT 1",
                (vehicle_id,),
            ).fetchone()
        return row is not None

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM diagnostic_events")
            connection.execute("DELETE FROM telemetry")
