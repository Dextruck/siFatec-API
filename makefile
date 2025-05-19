start-dev:
	uvicorn app.main:app --reload

start:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

up:
	docker compose -f .docker/docker-compose.yml up -d --build --force-recreate --remove-orphans db

stop:
	docker compose -f .docker/docker-compose.yml down -v --remove-orphans