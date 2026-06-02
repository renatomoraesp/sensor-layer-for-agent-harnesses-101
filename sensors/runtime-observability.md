---
id: runtime-observability
name: Runtime Evidence and Observability Sensor
version: 0.1.0
trigger:
  - after_runtime_check
  - after_command_failure
  - before_done
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - runtime_logs
    - command_output
    - expected_runtime_behavior
  optional:
    - e2e_transcript
    - browser_trace
    - health_checks
    - screenshots
    - diff
non_goals:
  - guessing without runtime signals
  - replacing instrumentation
  - broad performance profiling
---

# Runtime Evidence and Observability Sensor

## Purpose

Interpret runtime signals and decide whether they support the agent's claims.
When they do not, localize the likely failing boundary and identify the next
diagnostic or repair step.

## Evidence to inspect

- Runtime logs, command output, traces, transcripts, screenshots, and health
  checks.
- Expected runtime behavior from the task or docs.
- Relevant diff and configuration changes.
- Repeated failure history, if available.

## Judgment rubric

Return `PASS` when runtime evidence shows the claimed behavior actually
executed through the relevant boundary and no unresolved runtime errors remain.

Return `WARN` when runtime evidence is partial, manually observed, missing a
critical boundary, or enough for a tentative diagnosis but not enough for
completion.

Return `FAIL` when the runtime evidence contradicts the claim, no runtime
verification exists for behavior that requires it, or the agent is editing
without responding to the real failure signal.

Return `ERROR` only when configured runtime evidence cannot be read or command
output is malformed in a way that prevents diagnosis.

## Output contract

Emit one `sensor-result.v1` JSON object. Identify the likely failing boundary
using available signals, separate observed facts from inference, and recommend
the next instrumentation, verification, or repair action.
