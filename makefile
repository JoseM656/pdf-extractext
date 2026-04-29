.PHONY: mongo server start stop remove install

CONTAINER_NAME = mongodb-pdf
MONGO_IMAGE    = mongo:7
MONGO_PORT     = 27017

mongo:
	docker run -d --name $(CONTAINER_NAME) -p $(MONGO_PORT):27017 $(MONGO_IMAGE)

server:
	uv run uvicorn dev.servers.app:app --reload

start:
	docker start $(CONTAINER_NAME)

stop:
	docker stop $(CONTAINER_NAME)

remove:
	docker stop $(CONTAINER_NAME) && docker rm $(CONTAINER_NAME)

install:
	uv sync