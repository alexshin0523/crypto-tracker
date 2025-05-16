COMPOSE = docker compose

.PHONY: up down logs restart ingestor build

up:                ## Start all containers in detached mode
	$(COMPOSE) up -d

down:              ## Stop containers and remove volumes
	$(COMPOSE) down -v

logs:              ## Follow all container logs
	$(COMPOSE) logs -f

restart:           ## Recreate containers after a change
	$(COMPOSE) down -v
	$(COMPOSE) pull
	$(COMPOSE) up -d

ingestor:
	$(COMPOSE) build ingestor
	$(COMPOSE) up -d ingestor

aggregator:
	$(COMPOSE) build aggregator
	$(COMPOSE) up -d aggregator