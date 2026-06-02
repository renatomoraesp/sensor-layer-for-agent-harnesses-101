# Customizing Existing Sensors

Customize a sensor by tightening evidence requirements, adding repository-local
terminology, or naming known architectural boundaries. Avoid weakening the core
question the sensor answers.

Good customizations:

- Add the target repo's feature-state file path.
- Name required runtime commands for a specific workflow.
- Include local architecture invariants.

Risky customizations:

- Removing required evidence because it is inconvenient.
- Turning a bounded sensor into a generic AI review prompt.
- Letting a sensor pass when checks were skipped without explanation.
