# Writing New Sensors

A sensor should answer one bounded question over explicit evidence. It should
not be a generic "review this code" prompt.

## Complete Card Example

```markdown
---
id: migration-readiness
name: Migration Readiness Sensor
version: 0.1.0
trigger:
  - pre_pr
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - task
    - diff
    - test_results
    - runtime_logs
  optional:
    - rollback_plan
non_goals:
  - full database audit
---

# Migration Readiness Sensor

## Purpose

Determine whether a schema migration is safe to submit with the available
verification and rollback evidence.

## Judgment rubric

Return `PASS` only when migration tests, clean-environment execution, and
rollback evidence support the claim.

Return `WARN` when the migration is plausible but rollback or runtime evidence
is thin.

Return `FAIL` when required migration evidence is missing or contradictory.

Return `ERROR` only when the sensor cannot read required evidence.

## Output contract

Emit one `sensor-result.v1` JSON object with concrete repair steps.
```

## Bad Generic Prompt

```markdown
# Review This PR

Tell me if anything looks wrong.
```

This is not a sensor. It has no trigger, evidence contract, pass/fail semantics,
or repair shape.

## Narrowed Good Version

Ask a specific question instead: "Do the migration tests and runtime evidence
justify marking this migration ready for review?"

## Required vs Optional Evidence

Required evidence is needed for the sensor's core judgment. Optional evidence
can strengthen confidence but should not be necessary for every target repo.

If required evidence is often unavailable, the sensor is probably too broad or
belongs later in the target repo's maturity path.

## Verdict Semantics

- `PASS`: evidence supports the bounded claim.
- `WARN`: evidence is plausible but weak, partial, or policy-dependent.
- `FAIL`: a blocking gap or contradiction exists.
- `ERROR`: the sensor could not run correctly.

## Adding an Eval Case

1. Create `evals/cases/<case-name>/evidence.json`.
2. Create `evals/expected/<case-name>.json`.
3. Use `sensor-result.v1`.
4. Run:

   ```bash
   python -m harness_sensors eval --case <case-name>
   ```

## Adding Tests

Add Python tests when the sensor changes runtime behavior, schema expectations,
prompt rendering, or eval structure. Sensor wording changes should update eval
cases when they alter expected judgment.
