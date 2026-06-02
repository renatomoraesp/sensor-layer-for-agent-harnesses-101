# Clone and Port

This guide is written for a coding agent adapting Harness Sensors into another
repository. Keep the first port small: install the state surface, render one
prompt, and prove the workflow before customizing every card.

## When to Use Prompt-Only Mode

Use prompt-only mode first. It requires no API keys, makes no network calls, and
writes the rendered prompt to `.harness/prompts/` so a human or external model
can inspect it.

Prompt-only mode is the right default when:

- the target repo has not adopted harness state files yet;
- sensor cards are being customized;
- a team wants to review the exact prompt before provider-backed runs;
- CI should collect evidence but not call a model.

Prompt-only `run` intentionally returns `WARN`. That means "no inferential
judgment was invoked," not that the product code is risky by itself.

## When to Configure a Provider

Configure a provider only after prompt-only output looks right and the target
repo has reliable evidence paths. Provider-backed mode is useful for repeated
checks before PRs, but the provider result should still be recorded as
`sensor-result.v1` and reviewed like any other quality signal.

Provider-backed mode should not be the first adoption step.

## Porting Steps

1. Install the template:

   ```bash
   python -m harness_sensors install --repo . --profile minimal
   ```

2. Edit `harness/feature_list.json` so it names the real active feature.

3. Edit `harness/sprint_contract.md` so it defines the objective, allowed scope,
   required checks, and exit criteria.

4. Adapt `AGENTS.md`. Keep it short. It should point agents to harness state
   files and local architecture docs instead of becoming a rule dump.

5. Create a target config from `configs/target-repo.example.yaml`. Fill in test,
   build, lint, runtime, health-check, log, and docs paths.

6. Run:

   ```bash
   python -m harness_sensors doctor --repo .
   python -m harness_sensors doctor --repo . --strict --json
   ```

7. Render the first prompt:

   ```bash
   python -m harness_sensors render --repo . --sensor completion-calibration
   ```

8. Record the result. If the prompt is pasted into a model, save the returned
   `sensor-result.v1` summary in `harness/quality_score.md` and the repair plan
   in `harness/progress.md`.

9. Commit harness files separately from product-code changes. This makes review
   easier and prevents harness adoption from hiding feature work.

## Defining an Active Feature

Use one active feature unless the sprint contract explicitly allows otherwise:

```json
{
  "schema_version": "harness-feature-list.v1",
  "active_feature": "F001",
  "features": [
    {
      "id": "F001",
      "title": "Implement checkout validation",
      "status": "in_progress",
      "active": true,
      "acceptance_criteria": [
        "Valid checkout creates a payment session",
        "Invalid cart is rejected"
      ],
      "verification": [],
      "completion_claim": null,
      "notes": ""
    }
  ]
}
```

The sensors use this record to derive task evidence, changed-file scope, missing
verification, and completion-claim risk.

## Recording Sensor Results

Use `harness/quality_score.md` for the latest status table and
`harness/progress.md` for repair actions. A failed sensor should leave a durable
record of:

- sensor id;
- status;
- missing evidence;
- next action;
- whether a human approved an exception.
