# Agent Operating Guide

Before changing code, read these files in order:

1. `harness/sprint_contract.md`
2. `harness/feature_list.json`
3. `harness/progress.md`
4. Local docs near the files you will edit
5. Architecture docs, if this repository has them

Keep work bounded to the active feature. Do not mark work complete unless the
relevant harness sensors pass, or a human-approved exception and its evidence are
recorded in `harness/progress.md`.

Record durable decisions in `harness/decisions.md`; do not rely on chat history
for future agents to recover context.
