# Troubleshooting

## Missing Harness Files

Run:

```bash
python -m harness_sensors doctor --repo . --strict --json
```

Install templates with:

```bash
python -m harness_sensors install --repo . --profile minimal
```

## Malformed Sensor Frontmatter

Sensor cards must start with YAML frontmatter and include `## Judgment rubric`
and `## Output contract`. Run `doctor` after edits.

## Provider API Failures

Provider failures become `ERROR` sensor results. Confirm model, endpoint, and
API-key environment variables before treating provider-backed mode as reliable.

## Invalid Provider JSON

The runner expects one `sensor-result.v1` JSON object. If a provider wraps JSON
in prose, the runner will attempt extraction, then return `ERROR` if validation
fails.

## Missing Runtime Logs

Configured but absent logs are reported as missing. This is often a legitimate
`WARN` or `FAIL` for Runtime Observability.

## Tests Configured But Not Run

Configured commands show as `present_not_run` until `--run-checks` is used or
external command output is attached. Sensors should not treat `not_run` as
passing evidence.

## Noisy Diffs

Use Feature-State and WIP Boundary. Revert, split, or explicitly classify
unrelated changes before review.

## Prompt Too Large

Reduce configured docs/log paths, attach concise transcripts, or split the task.
Do not weaken the sensor by hiding required evidence.

## Prompt-Only Returns WARN

This is by design. Prompt-only mode rendered a prompt and skipped model
judgment. Paste the prompt into a model or configure a provider if you need an
inferential result.
