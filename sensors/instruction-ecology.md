---
id: instruction-ecology
name: Instruction Ecology Sensor
version: 0.1.0
trigger:
  - docs_changed
  - scheduled
  - after_repeated_sensor_failure
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - agents_md
    - harness_docs
    - changed_documentation
  optional:
    - module_docs
    - recent_sensor_failures
    - feature_state
maturity: maturity
non_goals:
  - making AGENTS.md a rule landfill
  - replacing architecture documentation
  - optimizing documentation aesthetics
---

# Instruction Ecology Sensor

## Purpose

Evaluate whether harness instructions are concise, non-contradictory, close to
the code they constrain, and still aligned with current repository behavior.
This is a maturity-level sensor for keeping the harness itself healthy.

## Evidence to inspect

- `AGENTS.md`, harness docs, module-local docs, and architecture docs.
- Changed documentation files.
- Recent repeated sensor failures or recurring agent mistakes.
- Feature state and progress files when they reveal stale instructions.

## Judgment rubric

Return `PASS` when instructions are short, discoverable, non-duplicative, and
placed at the right level of specificity.

Return `WARN` when documentation is useful but starting to drift, duplicate
itself, or accumulate rules that belong closer to a module or deterministic
check.

Return `FAIL` when instructions contradict one another, are too vague to follow,
hide important workflow constraints, or have become stale relative to code and
sensor behavior.

Return `ERROR` only when the instruction files needed for judgment cannot be
read.

## Output contract

Emit one `sensor-result.v1` JSON object. Recommend consolidation, relocation,
deletion, or conversion into deterministic checks or narrower sensor cards. Keep
repairs concrete and avoid generic documentation advice.
