# Claude Code

Claude Code can use the sensor cards as copyable review rubrics. Keep the core
workflow file-based:

```bash
python -m harness_sensors render --repo . --sensor test-adequacy
```

Then provide the rendered prompt to Claude Code as a focused review request.
Keep completion decisions tied to `sensor-result.v1` output rather than vague
chat approval.
