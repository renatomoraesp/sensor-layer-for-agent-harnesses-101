# Sensor Cards

Sensor cards are the first-class implementation surface in this repository.
Each card defines one inferential feedback control: when it runs, what evidence
it needs, how it judges that evidence, and what structured result it must emit.

Cards are markdown so they can be copied into target repositories and read by
humans or coding agents without opening Python internals. The YAML frontmatter
is validated by the runtime; the body is the rubric used to render prompts.

Run a prompt-only sensor from a checkout with:

```bash
python -m harness_sensors render --repo /path/to/target --sensor test-adequacy
python -m harness_sensors run --repo /path/to/target --sensor completion-calibration
```

Every card must keep a narrow responsibility, name required evidence, define
PASS/WARN/FAIL semantics, and ask for concrete repair instructions.
