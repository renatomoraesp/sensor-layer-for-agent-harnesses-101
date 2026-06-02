# Harness Sensors

A small, inspectable sensor layer for coding-agent harnesses.

Harness Sensors asks one practical question after an agent has worked on a
repository:

> Does the available evidence actually support the agent's claim?

Tests, linters, and type checkers are still essential. This project sits beside
them. It collects evidence from a target repository, renders focused
provider-neutral prompts from markdown sensor cards, and expects structured
`sensor-result.v1` feedback that tells the next agent or human reviewer what to
repair.

It is intentionally not a coding agent, IDE plugin, benchmark suite, autonomous
review bot, production observability platform, or CI replacement.

## Why This Exists

Coding agents can produce useful work while still leaving behind subtle harness
failures:

- A feature is marked done, but the acceptance criteria were not verified.
- Tests pass, but only exercise the happy path or the wrong behavior.
- A change works locally, but violates an architecture boundary.
- A runtime-sensitive feature has no runtime logs, transcript, or health check.
- A session ends with dirty state and no clear handoff for the next agent.

Harness Sensors treats those failures as feedback-control problems. The project
does not try to make the agent smarter by adding more rules up front. It gives
the harness a small sensor layer that can inspect what happened and return
repair-oriented feedback.

## What Is In The Box

- Markdown sensor cards in [sensors/](sensors/) with YAML frontmatter, evidence
  requirements, judgment rubrics, and strict output contracts.
- A thin Python runtime in [src/harness_sensors/](src/harness_sensors/) for
  loading cards, collecting evidence, rendering prompts, calling optional
  providers, and writing reports.
- A portable target-repo harness template in
  [templates/target-repo/](templates/target-repo/).
- Provider adapters for prompt-only mode, OpenAI Responses, Anthropic Messages,
  and local OpenAI-compatible chat-completions endpoints.
- Offline eval cases in [evals/](evals/) that validate seeded sensor examples
  structurally.
- Example target repositories and sample reports in [examples/](examples/).

The first-class product surface is the sensor card, not the Python internals.
The runtime is deliberately boring glue around readable, copyable controls.

## Status

This is a minimal open-source reference implementation for people exploring new
ways to build with coding-agent harnesses. It is meant to be read, adapted, and
ported into other repositories. It is not presented as a production-grade
product.

The safest starting mode is prompt-only mode. Prompt-only mode makes no network
calls, writes the rendered prompt to disk, and returns a `WARN` placeholder that
explicitly says no model judgment was invoked.

## Quick Start

From a checkout:

```bash
poetry install
poetry run python -m harness_sensors run --repo examples/python-api-small --sensor completion-calibration
poetry run python -m harness_sensors render --repo examples/python-api-small --sensor test-adequacy
poetry run python -m harness_sensors eval --all
```

That path exercises the small Python example in prompt-only mode. The `run`
command writes a prompt-only `WARN` result, and the `render` command writes the
model-ready prompt.

To see strict setup validation, architecture docs, runtime evidence, and richer
harness state:

```bash
poetry run python -m harness_sensors doctor --repo examples/fastapi-service --strict --json
poetry run python -m harness_sensors render \
  --repo examples/fastapi-service \
  --config configs/target-repo.example.yaml \
  --sensor runtime-observability \
  --out examples/fastapi-service/.harness/prompts/runtime-observability.prompt.md
```

Open the rendered prompt and inspect the evidence bundle, evidence availability
summary, sensor card, and output schema. That is the core artifact this project
is trying to make useful.

## How It Works

1. Load sensor cards from `sensors/`.
2. Collect an `evidence-bundle.v1` from the target repository.
3. Derive compact summaries such as active task, changed-file classification,
   and evidence availability.
4. Render a provider-neutral prompt containing the sensor card, evidence, and
   `sensor-result.v1` schema.
5. In prompt-only mode, write the prompt to `.harness/prompts/`.
6. With a provider configured, call the model and validate the returned result.
7. Write markdown, JSONL, GitHub summary, or agent-repair output.

By default, configured test, build, lint, runtime, health, and end-to-end
commands are recorded as available commands but are not executed. Pass
`--run-checks` when you want the runtime to execute those commands and capture
their output.

## Core Sensors

Harness Sensors ships six core sensors. One maturity-level sensor is available
but does not run by default.

| Sensor | What It Checks |
| --- | --- |
| `completion-calibration` | Whether a completion claim is supported by acceptance criteria and verification evidence. |
| `feature-wip-boundary` | Whether the diff stays inside the active feature and avoids hidden scope expansion. |
| `test-adequacy` | Whether tests meaningfully exercise the behavior being claimed. |
| `architecture-drift` | Whether the change preserves documented architecture and module boundaries. |
| `runtime-observability` | Whether runtime-sensitive work has logs, health checks, transcripts, or equivalent evidence. |
| `clean-handoff` | Whether the repository state is clean enough for the next agent or human to continue. |
| `instruction-ecology` | Optional maturity sensor for conflicting, stale, or overloaded instructions. |

Run all default core sensors with:

```bash
poetry run python -m harness_sensors run --repo examples/python-api-small --all
```

Enable maturity or experimental sensors explicitly in config when a target repo
has enough harness discipline to support them.

## Evidence Model

The runtime collects a compact, serializable `evidence-bundle.v1`. Depending on
configuration and target-repo state, it can include:

- active feature, acceptance criteria, verification, and completion claims;
- Git status, changed files, staged and unstaged diffs;
- changed-file classification for production code, tests, docs, and harness
  state;
- test, build, lint, runtime, health-check, and end-to-end command evidence;
- `AGENTS.md`, architecture docs, module docs, and harness docs;
- progress notes, decisions, sprint contract, and quality score;
- runtime logs, transcripts, traces, and missing-log paths;
- workspace cleanliness, temporary files, and TODO/FIXME markers;
- evidence availability summaries tailored to each sensor.

Missing evidence is represented explicitly. A sensor can then decide whether the
absence is acceptable, risky, or blocking.

## Result Contract

Every sensor result validates against `sensor-result.v1`:

```json
{
  "schema_version": "sensor-result.v1",
  "sensor_id": "test-adequacy",
  "status": "WARN",
  "confidence": 0.74,
  "summary": "Tests cover the main path but do not exercise the failure case named in the acceptance criteria.",
  "findings": [
    {
      "severity": "warning",
      "claim": "The behavior claim is only partially supported.",
      "evidence": [
        {
          "path": "harness/feature_list.json",
          "detail": "Acceptance criteria include invalid-input handling."
        }
      ],
      "repair": "Add a test for invalid input before marking the feature done."
    }
  ],
  "missing_evidence": ["negative-path test output"],
  "next_actions": ["Add the missing test and re-run the sensor."],
  "metadata": {}
}
```

Statuses are `PASS`, `WARN`, `FAIL`, and `ERROR`. Findings use `info`,
`warning`, `error`, and `blocker` severity.

## Adopting Another Repository

Install the minimal harness state surface into a target repository:

```bash
poetry run python -m harness_sensors install --repo ../my-target-repo --profile minimal
```

Then, in the target repo:

1. Fill out `harness/feature_list.json` with the active feature.
2. Fill out `harness/sprint_contract.md` with scope, required checks, and exit
   criteria.
3. Keep `harness/progress.md`, `harness/decisions.md`, and
   `harness/quality_score.md` current enough for a fresh agent to resume.
4. Copy and adapt `configs/target-repo.example.yaml` so the runtime knows the
   repo's tests, docs, architecture docs, runtime logs, and check commands.
5. Run strict setup validation:

   ```bash
   python -m harness_sensors doctor --repo . --config harness-sensors.yaml --strict --json
   ```

6. Render one prompt-only sensor before enabling provider-backed runs:

   ```bash
   python -m harness_sensors render --repo . --config harness-sensors.yaml --sensor completion-calibration
   ```

Start small. A good first port usually runs one or two sensors well rather than
pretending every target repo has mature evidence for every control.

For a fuller walkthrough, see
[docs/adaptation/clone-and-port.md](docs/adaptation/clone-and-port.md),
[docs/adaptation/target-repo-contract.md](docs/adaptation/target-repo-contract.md),
and [docs/adaptation/configuring-evidence.md](docs/adaptation/configuring-evidence.md).

## Provider Configuration

Prompt-only mode is the default:

```yaml
provider:
  name: prompt-only
```

Provider-backed mode can use OpenAI, Anthropic, or a local OpenAI-compatible
endpoint:

```yaml
provider:
  name: openai
  model: gpt-4.1
  api_key_env: OPENAI_API_KEY
  endpoint: https://api.openai.com/v1/responses
```

```yaml
provider:
  name: local
  model: local-model
  endpoint: http://localhost:11434/v1/chat/completions
```

Provider results are runtime inputs, not magic truth. Keep the rendered prompt,
evidence bundle, and structured result reviewable.

## Evaluation Cases

The eval runner is intentionally modest. It validates seeded cases, expected
`sensor-result.v1` files, prompt rendering, and structural coverage. It is not a
claim that the project is a benchmark.

```bash
poetry run python -m harness_sensors eval --all
poetry run python -m harness_sensors eval --case weak-tests --json
```

The current cases include fail and pass or warn examples for each core sensor.

## Integration Notes

- [docs/integrations/github-actions.md](docs/integrations/github-actions.md)
  shows a small CI template.
- [docs/integrations/codex.md](docs/integrations/codex.md),
  [docs/integrations/claude-code.md](docs/integrations/claude-code.md),
  [docs/integrations/cursor.md](docs/integrations/cursor.md), and
  [docs/integrations/continue-checks.md](docs/integrations/continue-checks.md)
  sketch ways to use rendered sensor prompts with common coding-agent surfaces.
- [templates/continue/checks/](templates/continue/checks/) contains copyable
  Continue check prompts.

## Repository Map

| Path | Purpose |
| --- | --- |
| [sensors/](sensors/) | Canonical sensor cards. |
| [src/harness_sensors/](src/harness_sensors/) | Python runtime, evidence collectors, providers, reporters, and schemas. |
| [templates/target-repo/](templates/target-repo/) | Minimal harness files to copy into target repos. |
| [configs/](configs/) | Example sensor, provider, and target-repo configuration. |
| [docs/](docs/) | Concepts, adaptation guides, decisions, and integrations. |
| [examples/](examples/) | Small target repositories and sample reports. |
| [evals/](evals/) | Offline structural eval cases and expected results. |
| [tests/](tests/) | Runtime and fixture tests. |

Start with [docs/00-start-here.md](docs/00-start-here.md) for the conceptual
model, then read
[docs/concepts/computational-vs-inferential.md](docs/concepts/computational-vs-inferential.md)
for the core distinction this project is built around.

## Development

```bash
poetry install
poetry run ruff format .
poetry run ruff check .
poetry run mypy src tests
poetry run pytest
poetry run python -m harness_sensors eval --all
```

When changing a sensor card, keep it narrow, name required evidence explicitly,
preserve `PASS`/`WARN`/`FAIL`/`ERROR` semantics, and update eval cases when the
expected judgment changes.

## License

MIT. See [LICENSE](LICENSE).
