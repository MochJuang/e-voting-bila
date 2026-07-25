start:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

seed:
	python seed.py

# Migrasi + seed sekaligus
setup: migrate seed
