# Computational vs Inferential Checks

Computational checks are deterministic. A test runner, linter, type checker, or
dependency rule can produce reliable mechanical facts.

Inferential sensors consume those facts and ask whether they are sufficient.
For example, `pytest` can pass while the tests only assert that a component
renders. The Test Adequacy sensor can still fail because no behavior-level test
exercises the user-visible workflow.

Both layers matter. Harness Sensors does not replace computational checks; it
uses their output as evidence.
