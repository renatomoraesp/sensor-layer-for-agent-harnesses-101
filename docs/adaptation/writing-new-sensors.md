# Writing New Sensors

Create a markdown file in `sensors/` with YAML frontmatter and a focused body.

Required frontmatter fields:

- `id`
- `name`
- `version`
- `trigger`
- `sensor_type: inferential_feedback_control`
- `output_schema: sensor-result.v1`
- `evidence.required`
- `evidence.optional`
- `non_goals`

The body must include `## Judgment rubric` and `## Output contract`. A good
sensor asks one bounded question and produces actionable repair instructions. A
bad sensor says "review the code" without naming evidence, pass/fail semantics,
or concrete next actions.
