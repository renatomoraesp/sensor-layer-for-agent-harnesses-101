# Evals

These are small seeded failure cases for the sensor cards, evidence bundling, and
output schema. They are not a benchmark suite. Each case contains enough context
to exercise one core sensor failure mode offline.

Run all cases:

```bash
python -m harness_sensors eval --all
```

Run one case:

```bash
python -m harness_sensors eval --case weak-tests
```

The offline eval runner validates each evidence bundle, validates the expected
`sensor-result.v1`, renders the matching sensor prompt, and checks structural
properties. It does not claim that prompt-only mode produced an inferential
verdict.
