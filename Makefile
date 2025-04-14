VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PYTHONPATH := $(shell pwd)

# Create virtual environment and install dependencies
setup:
	python3.9 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -U pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	echo "Virtual environment created. Activate it with: source $(VENV_DIR)/bin/activate"

# Run the FastAPI server
run:
	$(VENV_DIR)/bin/uvicorn src.main:app --reload

# Clean up the environment
clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/*/__pycache__
	rm -f defi_yields.db

# Run tests
test:
	pytest

# Generate Postman collection
generate-postman:
	$(VENV_DIR)/bin/python scripts/generate_postman.py

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-logs-api:
	docker-compose logs -f api

docker-logs-worker:
	docker-compose logs -f worker

docker-logs-redis:
	docker-compose logs -f redis

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v
	docker-compose rm -f

.PHONY: setup run test clean generate-openapi generate-postman docker-build docker-up docker-down docker-logs docker-logs-api docker-logs-worker docker-logs-redis docker-restart docker-clean
