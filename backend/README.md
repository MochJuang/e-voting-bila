# Backend Structure

FastAPI backend for the e-voting mockup.

## Goals

- Use MySQL as the primary database.
- Support face enrollment and verification with InsightFace.
- Match the frontend mockup flow and route names.

## Proposed Layout

```text
backend/
  app/
    api/
      v1/
        endpoints/
    core/
    crud/
    db/
    models/
    schemas/
    services/
    utils/
    main.py
  alembic/
  tests/
  .env.example
  requirements.txt
```

## Notes

- `models/` holds SQLAlchemy models.
- `schemas/` holds Pydantic request/response contracts.
- `services/` holds business logic such as face verification.
- `api/v1/endpoints/` holds route handlers grouped by feature.
- `db/` holds database session and base model wiring.
- `alembic/` is reserved for migrations.

