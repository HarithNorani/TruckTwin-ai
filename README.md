# TruckTwin AI

TruckTwin AI is a synthetic, safety-conscious software-defined vehicle
prototype. It generates truck telemetry, validates incoming messages, detects
diagnostic conditions, and exposes the current vehicle state through a REST API.

The project intentionally uses synthetic data only. It is an engineering
support prototype: diagnostic rules produce investigation events, but the
system does not control a vehicle or make safety-critical decisions.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn trucktwin.api:app --reload
```

Then open the API documentation at <http://127.0.0.1:8000/docs>.
The engineering dashboard is available at <http://127.0.0.1:8000/dashboard>.

To generate one sample telemetry message:

```bash
trucktwin-simulator --vehicle-id truck-001
```

## Current MVP

- Pydantic-validated telemetry and diagnostic event models
- Deterministic simulator with normal and fault-injection modes
- SQLite-backed ingestion API for local development
- Browser dashboard for fleet state, telemetry, and diagnostic history
- Engine overheating, low brake pressure, and low battery voltage rules
- Unit and API tests

The next planned layer is a dashboard and cloud-ready time-series storage.

By default, the API stores data in `trucktwin.db`. Set `TRUCKTWIN_DB_PATH` to
use another SQLite file:

```bash
TRUCKTWIN_DB_PATH=/tmp/trucktwin.db uvicorn trucktwin.api:app --reload
```
