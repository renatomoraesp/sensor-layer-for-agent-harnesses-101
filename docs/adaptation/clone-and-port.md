# Clone and Port

You are adapting Harness Sensors into another repository.

1. Copy `templates/target-repo/harness/` into the target repo.
2. Copy the relevant sensor cards from `sensors/`.
3. Create `configs/sensors.yaml` from `configs/sensors.example.yaml`.
4. Fill in the target repo's test, build, lint, doc, and runtime commands.
5. Add the minimal `AGENTS.md` instructions from `templates/target-repo/AGENTS.md`.
6. Run `python -m harness_sensors doctor --repo .`.
7. Run one sensor in prompt-only mode.
8. Commit harness files separately from product-code changes.

Keep the first port small. Do not adapt every sensor at once if the target repo
does not yet have the state files or runtime evidence needed to support them.
