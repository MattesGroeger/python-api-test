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

# Monitoring
monitor-up:
	docker-compose -f docker-compose.monitoring.yml up -d

monitor-down:
	docker-compose -f docker-compose.monitoring.yml down

monitor-logs:
	docker-compose -f docker-compose.monitoring.yml logs -f

.PHONY: setup run test clean generate-postman monitor-up monitor-down monitor-logs
