# Harness Sensor Report

## runtime-observability

- Status: `WARN`
- Confidence: `0.74`
- Summary: Runtime logs show the endpoint reached the domain layer, but no full E2E transcript is attached.

### Findings

- **warning**: Service-level runtime evidence exists, but browser or API transcript evidence is partial.
  - Evidence: `examples/fastapi-service/.harness/logs/order-summary.log` - Request reached API and domain code.
  - Repair: Attach a full API transcript if completion depends on externally observable behavior.

### Next Actions

- Capture the endpoint transcript.
- Record the sensor result in `harness/quality_score.md`.
