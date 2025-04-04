VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PYTHONPATH := $(shell pwd)

# Create virtual environment and install dependencies
setup:
	python3.9 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -U pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	echo "Virtual environment created. Activate it with: source $(VENV_DIR)/bin/activate"

# Clean up the environment
clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/*/__pycache__
	rm -f defi_yields.db

.PHONY: setup run clean
