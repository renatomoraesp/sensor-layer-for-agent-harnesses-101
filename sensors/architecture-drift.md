---
id: architecture-drift
name: Architecture and Invariant Drift Sensor
version: 0.1.0
trigger:
  - after_diff
  - pre_pr
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - diff
    - changed_files
    - architecture_docs
    - neighboring_patterns
  optional:
    - import_rules
    - static_check_output
    - module_docs
non_goals:
  - broad redesign
  - style-only review
  - dependency policing without architectural reason
---

# Architecture and Invariant Drift Sensor

## Purpose

Evaluate whether a change preserves the intended shape of the repository. This
sensor catches semantic architecture drift that deterministic import checks may
miss.

## Evidence to inspect

- Current diff and changed-files list.
- Architecture docs, module-local docs, and existing neighboring patterns.
- Import rules or dependency checks when available.
- Newly introduced dependencies, abstractions, or boundary crossings.

## Judgment rubric

Return `PASS` when the change follows documented layering, reuses existing
abstractions, keeps domain decisions in the right layer, and introduces no
unjustified parallel patterns.

Return `WARN` when the change is probably acceptable but creates a new pattern,
boundary pressure, or dependency that should be documented or watched.

Return `FAIL` when business logic leaks into transport/UI/persistence layers,
domain concepts are duplicated, a documented invariant is violated in spirit, or
the implementation makes future worker/runtime paths inconsistent.

Return `ERROR` only when architecture evidence is missing or malformed enough
that no meaningful architecture judgment can be made.

## Output contract

Emit one `sensor-result.v1` JSON object. Name each violated invariant, cite the
evidence, explain why it matters, and give a concrete repair such as moving a
decision, extracting a command object, reusing an existing service, or updating
the documented boundary.
