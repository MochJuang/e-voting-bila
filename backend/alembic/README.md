# Alembic Migrations

This folder is reserved for database migration files.

Suggested setup:

- `alembic init alembic`
- point `env.py` to `app.core.database.Base.metadata`
- create revisions for `users`, `face_profiles`, `votes`, and admin tables

