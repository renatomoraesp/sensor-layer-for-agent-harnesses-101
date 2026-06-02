# Codex

Use Harness Sensors as a repository-local feedback layer for Codex sessions.

Recommended flow:

1. Ask Codex to read `AGENTS.md`, `harness/sprint_contract.md`, and
   `harness/feature_list.json`.
2. Make the intended code change.
3. Run deterministic checks normally.
4. Render a prompt-only sensor before declaring completion:

```bash
python -m harness_sensors run --repo . --sensor completion-calibration
```

Paste the rendered prompt back into a fresh model judgment when you want a
separate inferential review. Record failures and exceptions in
`harness/progress.md`.
