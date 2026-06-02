---
id: feature-wip-boundary
name: Feature-State and WIP Boundary Sensor
version: 0.1.0
trigger:
  - after_diff
  - before_done
  - pre_pr
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - active_feature
    - feature_list
    - sprint_contract
    - diff
    - changed_files
  optional:
    - ownership_map
    - module_boundaries
non_goals:
  - judging code quality outside the active scope
  - encouraging opportunistic refactors
  - replacing human scope decisions
---

# Feature-State and WIP Boundary Sensor

## Purpose

Check whether the agent stayed within the active feature, represented work state
truthfully, and avoided unrelated changes. This sensor protects reviewability
and resumability by keeping work bounded.

## Evidence to inspect

- Active feature, feature list, sprint contract, and acceptance criteria.
- Changed files and current Git diff.
- Any ownership, module-boundary, or allowed-scope notes.
- Feature-state updates, completion claims, and verification evidence.

## Judgment rubric

Return `PASS` when exactly one feature is active, changed files plausibly belong
to that feature, state files match the actual evidence, and no unrelated future
work appears in the diff.

Return `WARN` when the diff is probably in scope but the boundary evidence is
thin, the feature contract is vague, or small incidental cleanup needs explicit
classification.

Return `FAIL` when the agent started unrelated work, mixed multiple features,
changed state files dishonestly, introduced speculative abstractions, or marked
partial work as complete.

Return `ERROR` only when the feature-state evidence cannot be read or the sensor
cannot identify the relevant diff/state surface.

## Output contract

Emit one `sensor-result.v1` JSON object. For scope creep, identify the active
feature, the unrelated files or changes, why they fall outside the boundary, and
whether to revert, isolate, split, or reclassify them.
