# 0001: Markdown Sensor Cards

## Status

Accepted.

## Context

The repository is intended to be copied, read, and adapted by humans and coding
agents. A Python-only implementation would hide the most important product
surface from the main adoption workflow.

## Decision

Use markdown sensor cards with YAML frontmatter as the canonical sensor
interface. The frontmatter is machine-validated. The body remains readable,
copyable, and prompt-ready.

## Consequences

The runtime must parse and validate cards before execution. Sensor quality is
maintained through card rubrics, schemas, examples, and seeded eval cases rather
than through Python code alone.
