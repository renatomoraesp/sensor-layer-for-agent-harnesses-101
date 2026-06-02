# Repository Guidelines

This repository implements a minimal sensor layer for coding-agent harnesses.
Keep the public/copyable layer readable and keep the Python runtime thin.

## Orientation

- Start with `docs/00-start-here.md` for the concept.
- Sensor cards live in `sensors/` and are the first-class product surface.
- Runtime code lives in `src/harness_sensors/`.
- Target-repo adoption files live in `templates/target-repo/`.
- Seeded examples and reports live in `examples/` and `evals/`.

## Development

- Use Poetry for dependency and virtual environment management.
- Prefer `poetry run pytest` for tests.
- Prefer `poetry run ruff check .`, `poetry run ruff format .`, and
  `poetry run mypy src tests` for quality checks.
- Keep the package importable from a clean checkout.

## Sensor Changes

When adding or changing a sensor card:

1. Keep the card narrow and copyable.
2. Validate frontmatter against `sensor-card.v1`.
3. Name required and optional evidence explicitly.
4. Include `## Judgment rubric` and `## Output contract`.
5. Add or update tests, examples, or eval cases when behavior changes.

## Boundaries

- Do not build a coding agent or autonomous editing loop here.
- Do not make TDD itself a sensor.
- Do not hide the important product surface inside Python internals.
- Do not casually weaken output schemas, evidence requirements, or repair
  expectations.
