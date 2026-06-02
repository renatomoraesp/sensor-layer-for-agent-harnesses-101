# Harness Sensors

Harness Sensors is a minimal, portable sensor layer for coding-agent harnesses.
It is not a coding agent, an IDE plugin, a benchmark suite, or a CI replacement.
It provides small inferential feedback controls that inspect evidence from a
target repository and return structured, repair-oriented feedback before a human
reviewer has to catch the same issue.

The first-class artifact is the **sensor card**: a readable markdown file with
YAML frontmatter, evidence requirements, a judgment rubric, and a strict output
contract. The Python runtime exists to discover cards, collect evidence, render
provider-neutral prompts, optionally call a provider, and write reports.

## What A Sensor Does

A deterministic check can say `pytest passed`. An inferential sensor can say the
passing tests do not prove the claimed behavior because the critical checkout,
runtime, handoff, or architecture boundary was never exercised.

Harness Sensors ships six core sensors plus one maturity-level sensor:

- Completion Calibration
- Feature-State and WIP Boundary
- Test Adequacy and Behavior
- Architecture and Invariant Drift
- Runtime Evidence and Observability
- Continuity and Clean-Handoff
- Instruction Ecology, optional

## Quick Start

Install dependencies from a checkout:

```bash
poetry install
```

Inspect a target repository in safe prompt-only mode:

```bash
poetry run python -m harness_sensors doctor --repo examples/python-api-small
poetry run python -m harness_sensors collect --repo examples/python-api-small
poetry run python -m harness_sensors render --repo examples/python-api-small --sensor test-adequacy
poetry run python -m harness_sensors run --repo examples/python-api-small --sensor completion-calibration
poetry run python -m harness_sensors eval --all
```

Install the minimal harness state surface into another repository:

```bash
python -m harness_sensors install --repo /path/to/target --profile minimal
```

Prompt-only mode is the safe default. It writes prompts under
`.harness/prompts/` and returns a `WARN` result that explicitly says no model
judgment was invoked.

Use strict doctor output for CI or agent-readable setup checks:

```bash
python -m harness_sensors doctor --repo . --strict --json
```

## Minimal Example

```bash
python -m harness_sensors render \
  --repo /path/to/target \
  --sensor completion-calibration \
  --out /path/to/target/.harness/prompts/completion.prompt.md
```

The rendered prompt contains the sensor card, a compact evidence bundle, and the
`sensor-result.v1` schema. Paste it into a capable model or configure a provider
adapter when you want automated execution.

## Repository Map

- `sensors/`: canonical markdown sensor cards.
- `src/harness_sensors/`: thin Python runtime.
- `templates/target-repo/`: copyable harness files for adopting repositories.
- `docs/`: concepts, adaptation guidance, and integrations.
- `examples/`: small target repositories and generated reports.
- `evals/`: seeded failure cases for sensor quality checks.

Start with [docs/00-start-here.md](docs/00-start-here.md), then use
[docs/adaptation/clone-and-port.md](docs/adaptation/clone-and-port.md) and
[docs/adaptation/configuring-evidence.md](docs/adaptation/configuring-evidence.md)
when copying the harness into another codebase.
