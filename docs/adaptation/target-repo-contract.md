# Target Repository Contract

Harness Sensors works best when the target repository provides durable state
that a fresh agent can read without chat history.

## Required Files

### `harness/feature_list.json`

Tracks active work, status, acceptance criteria, verification, and completion
claims.

```json
{
  "schema_version": "harness-feature-list.v1",
  "active_feature": "F001",
  "features": [
    {
      "id": "F001",
      "title": "Short human-readable title",
      "status": "in_progress",
      "active": true,
      "acceptance_criteria": [],
      "verification": [],
      "completion_claim": null,
      "notes": ""
    }
  ]
}
```

Field meanings:

- `active_feature`: the one feature the agent is currently allowed to advance.
- `status`: usually `todo`, `in_progress`, `blocked`, or `done`.
- `acceptance_criteria`: behavior the completion sensor and test-adequacy
  sensor should check against.
- `verification`: commands, runtime checks, transcripts, or sensor results that
  support the current state.
- `completion_claim`: the exact claim being evaluated before done/PR.

### `harness/progress.md`

Resumable session state. It should say what changed, what passed, what failed,
what remains, and the next concrete action.

### `harness/decisions.md`

Durable decisions future agents must preserve. Record architecture and
implementation choices here, not in chat only.

### `harness/sprint_contract.md`

The bounded objective. Include allowed scope, required checks, runtime evidence,
and exit criteria.

### `harness/quality_score.md`

Latest sensor outcomes. Keep this short and current.

### Target `AGENTS.md`

The table of contents for agents. It should point to the harness state files,
local docs, architecture docs, and sensor commands. It should not become a
large collection of generic rules.

## Optional But Valuable Files

- Architecture docs such as `docs/architecture.md`.
- Module-local docs near changed code.
- Runtime logs under `.harness/logs/` or another configured path.
- Generated outputs under `.harness/prompts/`, `.harness/evidence/`, and
  `.harness/reports/`.

Generated `.harness/` outputs are usually not committed. Commit curated example
reports only when they teach future agents something durable.
