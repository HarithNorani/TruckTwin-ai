import os
from typing import Optional

from fastapi import FastAPI, HTTPException, status

from .dashboard import dashboard_response
from .diagnostics import detect_events
from .models import DiagnosticEvent, TelemetryMessage
from .storage import TelemetryRepository


def create_app(repository: Optional[TelemetryRepository] = None) -> FastAPI:
    repository = repository or TelemetryRepository(
        os.getenv("TRUCKTWIN_DB_PATH", "trucktwin.db")
    )
    application = FastAPI(
        title="TruckTwin AI API",
        version="0.1.0",
        description="Synthetic telemetry and diagnostic API for a software-defined vehicle prototype.",
    )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/dashboard", include_in_schema=False)
    def dashboard() -> object:
        return dashboard_response()

    @application.post(
        "/telemetry", response_model=TelemetryMessage, status_code=status.HTTP_201_CREATED
    )
    def ingest_telemetry(message: TelemetryMessage) -> TelemetryMessage:
        repository.save_telemetry(message, detect_events(message))
        return message

    @application.get("/vehicles", response_model=list[str])
    def list_vehicles() -> list[str]:
        return repository.list_vehicles()

    @application.get("/vehicles/{vehicle_id}/telemetry", response_model=list[TelemetryMessage])
    def get_telemetry(vehicle_id: str) -> list[TelemetryMessage]:
        if not repository.has_vehicle(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return repository.telemetry_for(vehicle_id)

    @application.get("/vehicles/{vehicle_id}/events", response_model=list[DiagnosticEvent])
    def get_events(vehicle_id: str) -> list[DiagnosticEvent]:
        if not repository.has_vehicle(vehicle_id):
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return repository.events_for(vehicle_id)

    return application


app = create_app()
