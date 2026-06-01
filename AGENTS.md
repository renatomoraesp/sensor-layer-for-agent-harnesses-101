# Repository Guidelines

This repository is being prepared as a Python project for a sensor layer around agent harnesses. Keep changes small, explicit, and easy to inspect.

## Project Shape

- Runtime code lives under `src/sensor_layer_for_agent_harnesses_101/`.
- Tests live under `tests/`.
- Project metadata and tool configuration live in `pyproject.toml`.
- Local environment values belong in `.env`, with committed examples in `.env.example`.

## Development

- Use Poetry for dependency and virtual environment management.
- Prefer `poetry run pytest` for tests.
- Prefer `poetry run ruff check .`, `poetry run ruff format .`, and `poetry run mypy src tests` for code quality checks.
- Do not commit `.env`, virtual environments, caches, or generated coverage output.

## Style

- Keep the package importable from a clean checkout.
- Prefer typed, boring Python over clever abstractions.
- Add comments only when they clarify non-obvious intent.
