# Continue Checks

Continue Checks are source-controlled markdown checks for AI-assisted review.
Harness Sensors keeps its canonical cards in `sensors/` and can export a subset
to Continue-style check files:

```bash
python -m harness_sensors export continue --repo .
```

The export writes compatible checks to `.continue/checks/` by default. These
checks do not replace the provider-neutral runtime; they are an integration
target for repositories already using Continue.
