# Claim Pilot Core

Shared configuration, database utilities, exceptions, and core components for the Claim Pilot platform. Logging provided by `claim-pilot-logging`.

## Components

- **BaseSettings** — Pydantic Settings base class for all services to inherit
- **DatabaseConnection** — PostgreSQL wrapper with connection pooling
- **Exception Hierarchy** — `ClaimPilotError` base with `DatabaseError`, `ToolExecutionError`, `ValidationError`, `NotFoundError`, `PolicyNotFoundError`, `ClaimNotFoundError`
- **Logging Re-exports** — `get_logger`, `setup_logging`, `LogContext`, `timed` from claim-pilot-logging

## Installation

```bash
pip install claim-pilot-core
```

## Usage

```python
from claim_pilot_core import get_settings, get_logger, get_db, setup_logging
from claim_pilot_core.core import BaseSettings, create_settings

# Create service-specific settings
class MySettings(BaseSettings):
    ai_service_url: str = "http://localhost:9020"

settings = create_settings(MySettings)
logger = get_logger(__name__)
db = get_db()

rows = db.fetch_all("SELECT * FROM claims WHERE status = %s", ("submitted",))
```

## Local Development

```bash
pip install -e ".[dev]"
make test
make test-integration  # requires PostgreSQL
make lint
```

## Versioning

Calendar Versioning (CalVer): `YYYY.MM.PATCH`

## Maintainer

**Justin Weber** — Blue Lambda Technologies  

This repository is maintained for the **Claim Pilot** platform (Blue Lambda University).

- **Email:** [justin.weber@bluelambdatechnologies.com](mailto:justin.weber@bluelambdatechnologies.com)

For professional inquiries, security-sensitive reports, or questions about this component, please reach out via the address above.
