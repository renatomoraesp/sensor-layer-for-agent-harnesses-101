# Harness Sensor Report

## architecture-drift

- Status: `FAIL`
- Confidence: `0.84`
- Summary: Domain code imported transport request state.

### Findings

- **error**: Domain services must not depend on request objects.
  - Evidence: `examples/fastapi-service/scenarios/architecture-drift/README.md` - The flawed scenario describes request state entering domain code.
  - Repair: Extract request data in `src/api/` and pass plain values into `src/domain/`.

### Next Actions

- Keep domain functions framework-independent.
- Re-run `architecture-drift` before PR.
