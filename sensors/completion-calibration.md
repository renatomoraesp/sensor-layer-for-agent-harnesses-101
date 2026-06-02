---
id: completion-calibration
name: Completion Calibration Sensor
version: 0.1.0
trigger:
  - before_done
  - pre_pr
  - after_tests
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - task
    - diff
    - feature_state
    - test_results
  optional:
    - runtime_logs
    - e2e_transcript
    - completion_claim
non_goals:
  - style review
  - full security audit
  - architecture review beyond completion evidence
---

# Completion Calibration Sensor

## Purpose

Determine whether a coding agent's completion claim is justified by executable,
runtime, and repository-state evidence. This sensor exists because "tests
passed" or "the immediate error disappeared" is not the same thing as a task
being complete.

## Evidence to inspect

- The original task, active feature, sprint contract, or completion claim.
- The current diff, changed files, and feature-state records.
- Test, lint, build, and runtime evidence that was actually run.
- Skipped checks, unresolved TODOs, failing commands, and missing acceptance
  criteria.

## Judgment rubric

Return `PASS` only when the evidence supports the exact behavior claimed, the
active acceptance criteria are satisfied, relevant checks were actually run, and
the feature state is truthful.

Return `WARN` when completion is plausible but evidence is incomplete, shallow,
or indirect enough that a human reviewer should know the risk.

Return `FAIL` when the work is declared complete but required evidence is
missing, contradictory, unrelated to the claimed behavior, or when known
failures are ignored.

Return `ERROR` only when the sensor cannot execute because required input is
unreadable, malformed, or impossible to interpret.

## Output contract

Emit one `sensor-result.v1` JSON object. Include concrete missing evidence and
repair steps. Do not ask the agent to "review more carefully"; name the exact
verification, state correction, or follow-up command needed before completion is
credible.
