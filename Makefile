# Makefile for Airflow Docker Compose setup

# Default shell for Make
SHELL := /bin/bash

# Load .env file variables
# This is a common pattern but might not work on all Make versions/OSes directly for Docker Compose.
# Docker Compose itself loads .env by default.
# ifneq (,$(wildcard ./.env))
#     include .env
#     export
# endif

# Get the UID and GID of the current user (for Linux/macOS)
# For Windows/WSL, you might need to set AIRFLOW_UID manually in .env
# CURRENT_UID := $(shell id -u)
# CURRENT_GID := $(shell id -g)
# export AIRFLOW_UID ?= $(CURRENT_UID)
# export AIRFLOW_GID ?= $(CURRENT_GID)

# Default command
.PHONY: help
help:
	@echo "Usage: make [command]"
	@echo "Commands:"
	@echo "  build             Build or rebuild services"
	@echo "  up                Start services in detached mode"
	@echo "  down              Stop and remove containers, networks, volumes, and images created by 'up'"
	@echo "  stop              Stop services"
	@echo "  start             Start existing stopped services"
	@echo "  restart           Restart services"
	@echo "  logs              Follow log output"
	@echo "  logs-webserver    Follow webserver logs"
	@echo "  logs-scheduler    Follow scheduler logs"
	@echo "  ps                List containers"
	@echo "  init              Run the airflow-init service (db init, user create)"
	@echo "  clean             Remove stopped containers and dangling images/volumes"
	@echo "  shell             Access bash shell in the webserver container"
	@echo "  fernet-key        Generate a new Fernet key"
	@echo "  test              Run pytest for DAGs"

.PHONY: build
build:
	docker-compose build

.PHONY: up
up: build
	docker-compose up -d

.PHONY: down
down:
	docker-compose down -v --remove-orphans

.PHONY: stop
stop:
	docker-compose stop

.PHONY: start
start:
	docker-compose start

.PHONY: restart
restart:
	docker-compose restart

.PHONY: logs
logs:
	docker-compose logs -f

.PHONY: logs-webserver
logs-webserver:
	docker-compose logs -f airflow-webserver

.PHONY: logs-scheduler
logs-scheduler:
	docker-compose logs -f airflow-scheduler

.PHONY: ps
ps:
	docker-compose ps

.PHONY: init
init:
	@echo "Running Airflow initialization (DB init, user creation)..."
	docker-compose run --rm airflow-init
	@echo "Initialization complete. You might need to restart services if this is the first run: make restart"

.PHONY: clean
clean:
	docker-compose down --volumes --remove-orphans # More thorough cleanup
	docker system prune -af # Remove dangling images and build cache

.PHONY: shell
shell:
	docker-compose exec airflow-webserver bash

.PHONY: fernet-key
fernet-key:
	@echo "Generating Fernet key..."
	@python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

.PHONY: test
test:
	@echo "Running DAG tests..."
	# Ensure you have pytest and necessary dependencies in your local/virtual env
	# Or run inside a container that has the testing tools
	# Example: docker-compose run --rm airflow-webserver pytest /opt/airflow/tests
	pytest tests/