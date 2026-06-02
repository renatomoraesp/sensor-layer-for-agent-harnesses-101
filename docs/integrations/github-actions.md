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

## Install Modes

Use one of these in target repositories:

```bash
# Published package, once available
pip install harness-sensors

# Source repository
pip install git+https://github.com/renatomoraesp/sensor-layer-for-agent-harnesses-101.git

# Vendored copy inside target repo
pip install -e tools/harness-sensors
```

Until the package is published, the workflow template uses the GitHub install
mode and leaves the PyPI command as a comment.
