PROJECT_NAME=recognition_api

# Postgres

psql:
	@psql -U postgres

migrations:
	@alembic revision --autogenerate

migrate:
	@alembic upgrade head
