---
id: clean-handoff
name: Continuity and Clean-Handoff Sensor
version: 0.1.0
trigger:
  - session_end
  - before_checkpoint
  - pre_pr
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - progress
    - decisions
    - feature_list
    - git_status
    - test_results
    - workspace_state
  optional:
    - last_failure
    - todo_markers
    - untracked_artifacts
non_goals:
  - forcing a clean Git tree before every pause
  - replacing progress notes with chat memory
  - judging product strategy
---

# Continuity and Clean-Handoff Sensor

## Purpose

Decide whether a fresh agent or human could resume the work without verbal
explanation and without first cleaning up inherited entropy.

## Evidence to inspect

- `harness/progress.md`, `harness/decisions.md`, and `harness/feature_list.json`.
- Git status, diff, untracked files, and temporary artifacts.
- Latest test/build status and last known failing command.
- TODO/FIXME markers and handoff notes.

## Judgment rubric

Return `PASS` when state files truthfully describe what changed, what passed,
what failed, what remains, and the next concrete action; workspace artifacts are
classified; and a new agent could resume from files alone.

Return `WARN` when the handoff is mostly resumable but contains minor ambiguity,
unclassified TODOs, or stale status that should be cleaned before a longer pause.

Return `FAIL` when progress is vague, failures are not recorded, feature state is
untruthful, temporary files are unexplained, or the workspace would force the
next agent to rediscover basic context.

Return `ERROR` only when handoff state files cannot be read.

## Output contract

Emit one `sensor-result.v1` JSON object. Name the exact state files, commands,
or artifacts that must be updated before stopping, and include the next concrete
resume action when it can be inferred from evidence.
