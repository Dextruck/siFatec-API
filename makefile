start-dev:
	uvicorn app.main:app --reload

start:
	uvicorn app.main:app

up:
	docker compose -f .docker/docker-compose.yml up -d --build --force-recreate --remove-orphans db

stop:
	sudo docker compose -f .docker/docker-compose.yml down -v --remove-orphans