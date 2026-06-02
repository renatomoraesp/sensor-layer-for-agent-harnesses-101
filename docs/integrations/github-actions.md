# GitHub Actions

The target-repo template includes a prompt-only workflow at
`templates/target-repo/.github/workflows/harness-sensors.yml`.

Prompt-only CI is intentionally conservative: it can collect evidence and render
prompts without requiring API keys. Provider-backed CI can be added later by
configuring `configs/providers.yaml` and storing API keys as repository secrets.

Suggested first CI step:

```bash
python -m harness_sensors collect --repo .
python -m harness_sensors run --repo . --sensor completion-calibration --format github
```

Treat provider failures as `ERROR` results, not as passing review.
