---
id: test-adequacy
name: Test Adequacy and Behavior Sensor
version: 0.1.0
trigger:
  - after_tests
  - before_done
  - pre_pr
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - task
    - changed_tests
    - changed_production_code
    - test_results
  optional:
    - coverage_output
    - runtime_transcript
    - acceptance_criteria
non_goals:
  - replacing the test runner
  - demanding exhaustive coverage
  - enforcing a particular testing style
---

# Test Adequacy and Behavior Sensor

## Purpose

Evaluate whether the tests and verification evidence prove the behavior claimed
by the task. This sensor treats deterministic test results as evidence, not as a
complete semantic verdict.

## Evidence to inspect

- Original task, acceptance criteria, and completion claim.
- Changed production code and changed test files.
- Test command output, coverage output, and skipped tests.
- Runtime or end-to-end transcript when behavior spans integration boundaries.

## Judgment rubric

Return `PASS` when tests exercise the user-visible or system-visible behavior
that matters, cover important acceptance criteria, and leave little room for the
implementation to be broken while tests still pass.

Return `WARN` when tests cover the main behavior but miss meaningful edge cases,
failure paths, integration seams, or runtime verification that should be added
soon.

Return `FAIL` when tests are tautological, over-mocked, focused on rendering or
implementation details instead of behavior, omit central acceptance criteria, or
when no relevant tests were run.

Return `ERROR` only when test evidence is unreadable or contradictory in a way
that prevents judgment.

## Output contract

Emit one `sensor-result.v1` JSON object. When evidence is inadequate, name the
missing behavior-level tests or runtime checks and explain how the current tests
could pass while the feature remains broken.
