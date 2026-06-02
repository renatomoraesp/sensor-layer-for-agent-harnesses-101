# Verdicts and Severity

Every sensor returns `sensor-result.v1`.

Statuses:

- `PASS`: no blocking issue found.
- `WARN`: a non-blocking or policy-dependent issue exists.
- `FAIL`: a blocking issue exists.
- `ERROR`: the sensor could not run correctly.

Finding severities:

- `info`
- `warning`
- `error`
- `blocker`

Results should include confidence, a concise summary, evidence-backed findings,
missing evidence, and concrete next actions.
