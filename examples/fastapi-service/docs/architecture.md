# Architecture

This example uses three layers:

- `src/api/`: transport adapters that parse request-shaped input.
- `src/domain/`: business behavior over plain command/data objects.
- `src/persistence/`: repository functions and storage details.

Route handlers may import domain and persistence functions. Domain code must not
import transport request objects or web-framework types. This invariant is what
the Architecture Drift sensor is meant to preserve.
