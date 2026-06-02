# Evidence Model

The runtime passes sensors an `evidence-bundle.v1` object. It is intentionally
compact and serializable so a sensor run can be reproduced or audited.

The bundle may include:

- Git status, changed files, staged and unstaged diffs, branch, and commit.
- Test, build, and lint command output.
- `AGENTS.md`, harness docs, architecture docs, and module-local docs.
- Feature state, progress notes, decisions, sprint contract, and quality score.
- Runtime logs, traces, transcripts, and health-check output.
- Workspace cleanliness, TODO/FIXME markers, and temporary files.

Missing evidence should be represented explicitly. A sensor can then decide
whether the absence is acceptable, risky, or blocking.
