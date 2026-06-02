# Cursor

Use Cursor for editing and Harness Sensors for evidence-backed review gates.

Suggested setup:

- Copy `templates/target-repo/` into the target repo.
- Keep `harness/progress.md` current after meaningful edits.
- Render sensor prompts from the terminal inside Cursor.
- Paste the prompt into a separate chat when you want an independent judgment.

Avoid turning the sensor cards into broad "review this PR" prompts. Each card
should remain responsible for one failure mode.
