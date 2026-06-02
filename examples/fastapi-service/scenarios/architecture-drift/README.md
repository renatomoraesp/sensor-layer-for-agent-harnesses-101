# Architecture Drift Scenario

Flawed change: `src/domain/orders.py` imports a request object and reads headers
directly. Corrected change: `src/api/orders.py` extracts transport fields and
passes plain values into domain functions.

Relevant sensor: `architecture-drift`.
