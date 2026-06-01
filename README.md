# Sensor Layer for Agent Harnesses 101

Early-stage Python project for exploring how a lightweight sensor layer can observe, structure, and expose signals from agent harnesses.

The implementation is intentionally minimal for now. The repository is set up so the real work can start from a clean, typed, tested Python package instead of an empty folder.

## Setup

Install dependencies with Poetry:

```bash
poetry install
```

Create local environment configuration:

```bash
cp .env.example .env
```

The starter configuration uses:

```bash
SENSOR_LAYER_ENV=development
SENSOR_LAYER_LOG_LEVEL=INFO
```

## Checks

```bash
poetry run pytest
poetry run ruff check .
poetry run mypy src tests
```

Or run the combined target:

```bash
make check
```

## Status

Research and references are still being gathered. The package currently contains only the initial settings layer and project scaffolding.
