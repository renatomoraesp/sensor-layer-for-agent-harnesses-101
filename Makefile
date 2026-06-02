.PHONY: install format lint test typecheck check doctor render-example run-example evals

install:
	poetry install

format:
	poetry run ruff format .

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy src tests

test:
	poetry run pytest

check: lint typecheck test

doctor:
	poetry run python -m harness_sensors doctor --repo examples/python-api-small

render-example:
	poetry run python -m harness_sensors render --repo examples/python-api-small --sensor completion-calibration

run-example:
	poetry run python -m harness_sensors run --repo examples/python-api-small --sensor completion-calibration

evals:
	poetry run python -m harness_sensors eval --all
