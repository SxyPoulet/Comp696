.PHONY: help build up down logs clean test install-deps

help:
	@echo "Sales Intelligence Agent - Available Commands:"
	@echo "  make build         - Build Docker containers"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make clean         - Remove containers, volumes, and images"
	@echo "  make test          - Run tests"
	@echo "  make install-deps  - Install backend dependencies with Poetry"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-upgrade    - Upgrade database to latest migration"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Flower (Celery): http://localhost:5555"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all

test:
	cd backend && poetry run pytest -v

install-deps:
	cd backend && poetry install

db-migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend /bin/bash

redis-cli:
	docker-compose exec redis redis-cli

psql:
	docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db
