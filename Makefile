.PHONY: install dev test lint format typecheck clean setup

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/

clean:
	rm -rf .venv/ __pycache__/ .mypy_cache/ .ruff_cache/
	rm -rf *.egg-info/ dist/ build/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

setup: dev pre-commit
	pre-commit install

pre-commit:
	pre-commit install

all: lint typecheck test
