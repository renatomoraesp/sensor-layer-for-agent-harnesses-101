# Configuring Evidence

Evidence configuration tells the runtime what to collect before rendering a
sensor prompt. The runtime then derives task evidence, changed-file buckets, and
availability summaries so the model does not have to infer everything from raw
diffs.

## Commands

```yaml
target:
  test_commands:
    - pytest
  build_commands:
    - npm run build
  lint_commands:
    - ruff check .
  runtime_commands:
    - python -m app.healthcheck
  health_check_commands:
    - curl -f http://localhost:8000/health
  e2e_commands:
    - pytest tests/e2e
```

Commands are recorded as `not_run` unless `--run-checks` is passed. This is
intentional: configured commands are evidence that a check exists, not proof
that it ran.

## Paths

```yaml
target:
  harness_dir: harness
  docs_paths:
    - AGENTS.md
    - docs
    - harness
  architecture_doc_paths:
    - docs/architecture.md
  log_paths:
    - .harness/logs/api.log
  report_dir: .harness/reports
  prompt_dir: .harness/prompts
  evidence_dir: .harness/evidence
```

Missing configured paths are represented explicitly. For example, configured
runtime logs that do not exist become `configured_missing`, not `present`.

## Derived Evidence

The runtime derives:

- `task` from `harness/feature_list.json` and `harness/sprint_contract.md`;
- `diff_summary.changed_tests`;
- `diff_summary.changed_production_code`;
- `diff_summary.changed_docs`;
- `diff_summary.changed_harness_state`;
- `evidence_availability` for sensor-required evidence.

Rendered prompts include a sensor-specific evidence summary near the top.
