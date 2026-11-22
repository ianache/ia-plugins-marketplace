---
description: Start or resume the governed infrastructure workflow (greenfield, brownfield or evolution)
argument-hint: "[greenfield|brownfield|evolution] [requirements, Context Packs or paths]"
---
Invoke the `infrastructure-orchestrator` skill with: $ARGUMENTS

Classify the initiative as greenfield, brownfield or evolution, create the plan with `scripts/workflow.py`, and dispatch contract-bound tasks to the specialist skills. Specialists never mutate the plan; human gates require `human:<id>` approval evidence.
