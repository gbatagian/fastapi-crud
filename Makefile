venv:
	poetry install --no-root

run:
	docker compose up

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