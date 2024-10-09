venv:
	poetry install --no-root

run:
	docker compose up

run-db:
	docker compose up api_db

build:
	docker compose up --build 

down:
	docker compose down -v --remove-orphans

db-session:
	docker compose exec api_db psql -U postgres -d api

api-session:
	docker compose exec api bash

black:
	black api/

isort:
	isort api/

autoflake:
	autoflake api/

mypy:
	mypy api/
	
reformat: autoflake black isort

migrations:
	cd api/ && alembic upgrade head && cd -

new-migration:
	@if [ -z "$(m)" ]; then \
		echo "Error: Please provide a message for the migration."; \
		echo "Usage: make migration m=\"Your migration comment\""; \
		exit 1; \
	fi
	cd api/ && alembic revision --autogenerate -m "$(comment)" && cd -