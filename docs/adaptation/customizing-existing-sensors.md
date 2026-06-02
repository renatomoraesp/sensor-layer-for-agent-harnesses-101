# Customizing Existing Sensors

Customize sensors by adding local precision without weakening their purpose.

## Architecture Invariants

Before:

```markdown
Required evidence:
- architecture_docs
```

After:

```markdown
Required evidence:
- architecture_docs
- module_docs

Local invariant:
Domain services must receive command objects and must not import FastAPI,
Django, Flask, or request objects.
```

This strengthens the Architecture Drift sensor.

## Runtime Checks

Before:

```yaml
log_paths:
  - .harness/logs
```

After:

```yaml
runtime_commands:
  - curl -f http://localhost:8000/health
e2e_commands:
  - pytest tests/e2e/test_checkout.py
log_paths:
  - .harness/logs/api.log
```

This gives Runtime Observability more concrete evidence.

## Feature-State Conventions

Before:

```json
{"status": "done"}
```

After:

```json
{
  "status": "done",
  "verification": [
    {"command": "pytest tests/test_checkout.py", "status": "passed"},
    {"sensor": "completion-calibration", "status": "PASS"}
  ]
}
```

This makes Completion Calibration and Clean Handoff more reliable.

## Risky Customizations

Avoid:

- removing required evidence because it is inconvenient;
- turning a bounded card into broad PR review;
- letting skipped checks count as passing evidence;
- disabling maturity-level sensors by editing card metadata instead of config.
