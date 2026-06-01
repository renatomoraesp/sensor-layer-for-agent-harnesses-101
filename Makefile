.PHONY: install test lint format typecheck check

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy src tests

check: lint typecheck test
