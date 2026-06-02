# Target Repository Contract

A target repository works best when it provides a small durable state surface:

- `harness/feature_list.json` for active work, acceptance criteria, status, and
  verification evidence.
- `harness/progress.md` for resumable session state.
- `harness/decisions.md` for architecture and implementation decisions.
- `harness/sprint_contract.md` for current scope and exit criteria.
- `harness/quality_score.md` for latest sensor outcomes.

The target should also define test, build, lint, documentation, and runtime log
paths in config. Sensors can still run with partial evidence, but they should
warn or fail when missing evidence weakens a completion claim.
