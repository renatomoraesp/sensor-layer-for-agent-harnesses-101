# Sensors vs Guides

Guides are feedforward controls. They tell an agent what to read, what patterns
to preserve, and what the active objective is before the agent changes code.

Sensors are feedback controls. They observe evidence after an action and emit a
repair-oriented result.

`AGENTS.md`, architecture docs, feature lists, and sprint contracts are usually
guides or state artifacts. The markdown cards in `sensors/` are active
evaluators over evidence.
