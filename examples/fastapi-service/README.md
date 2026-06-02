# FastAPI-Service-Style Example

This is a small service-shaped target repository for demonstrating Harness
Sensors. It is intentionally dependency-light: the files use plain Python
functions instead of requiring FastAPI at test time, but the layout mirrors a
typical web service.

## Layout

- `src/api/`: request/response adapter layer.
- `src/domain/`: framework-independent business behavior.
- `src/persistence/`: storage-facing functions.
- `docs/architecture.md`: local architecture invariant.
- `.harness/logs/order-summary.log`: curated runtime evidence.
- `scenarios/`: intentionally flawed situations a sensor should catch.

## Demonstrated Sensors

- `architecture-drift`: domain code must not import request/web-framework state.
- `test-adequacy`: endpoint tests should assert behavior, not only existence.
- `runtime-observability`: runtime logs should prove the claimed flow executed.
- `clean-handoff`: harness state names next action and current evidence.

Run from the project root:

```bash
python -m harness_sensors doctor --repo examples/fastapi-service
python -m harness_sensors render --repo examples/fastapi-service --sensor architecture-drift
```
