# Sprint Contract

## Objective

Adopt the minimal harness-sensor state surface and use it to keep agent work
bounded and resumable.

## Allowed Scope

- Harness state files under `harness/`
- Sensor configuration under `configs/`, if copied into this repository
- Agent orientation instructions in `AGENTS.md`

## Required Checks

- Render at least one sensor prompt in prompt-only mode.
- Record test/build/lint evidence when product code changes.

## Exit Criteria

- Active feature state matches the real work.
- `harness/progress.md` names what changed, what passed, what failed, and the
  next action.
- Completion claims are backed by sensor or runtime evidence.
