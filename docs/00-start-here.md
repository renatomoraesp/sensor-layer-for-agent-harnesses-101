# Start Here

Harness Sensors provides inferential feedback controls for coding-agent
harnesses. A harness is the control environment around an agent: instructions,
state files, scripts, checks, evidence, runtime feedback, and review loops.

This repository focuses on **feedback** after the agent acts. It does not edit
code, plan work, or replace CI. It gathers evidence from a target repository,
combines that evidence with a markdown sensor card, and asks for a structured
judgment.

## Core Concepts

- Guides steer the agent before it acts: `AGENTS.md`, architecture docs, sprint
  contracts, feature lists, and local conventions.
- Computational sensors are deterministic checks: tests, linters, type
  checkers, import-boundary tools, and build commands.
- Inferential sensors are semantic feedback controls: they judge whether the
  evidence actually supports the agent's claim.

## Runtime Flow

1. Load sensor cards from `sensors/`.
2. Collect an `evidence-bundle.v1` from the target repository.
3. Render a provider-neutral prompt.
4. In prompt-only mode, write the prompt to disk.
5. With a provider configured, validate the returned `sensor-result.v1`.
6. Write markdown, JSONL, GitHub summary, or agent repair reports.

## Adoption Flow

Copy `templates/target-repo/` into a target project, adapt the feature state and
sprint contract, then render one prompt-only sensor before trusting automated
provider calls. See `docs/adaptation/clone-and-port.md`.
