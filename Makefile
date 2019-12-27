PROJECT_SERVICE=web
PROJECT_APP=tesseract_app
PROJECT_NAME=tesseract_api

# Docker
up:
	@docker-compose up $(PROJECT_SERVICE)

stop:
	@docker-compose stop

clean:
	@docker-compose down
	make clean_image

clean_image:
	@docker rmi $(PROJECT_NAME)_$(PROJECT_SERVICE)

bash:
	@docker exec -it $(PROJECT_APP) bash

docker-redis:
	@docker exec -it $(PROJECT_NAME)_redis_1 redis-cli

docker-psql:
	@docker exec -it $(PROJECT_NAME)_db_1 psql -U postgres


# Postgres
psql:
	@psql -U postgres

migrations:
	@alembic revision --autogenerate

migrate:
	@alembic upgrade head
