---
name: infrastructure-architecture-design
description: Topology, networking, sizing and FinOps. Internal specialist. Use only when dispatched by infrastructure-orchestrator with a task contract (task_id, execution_id, mode). For a user request to design or review infrastructure, use infrastructure-orchestrator instead.
---
# infrastructure-architecture-design

## Required workflow
1. Read `resources/input-contract.yaml`, `resources/output-contract.yaml`, `resources/gate-checklist.md` and the corporate standard reference.
2. Verify mode, task ID, execution ID, input artifact IDs, source provenance and baseline requirements.
3. Use the matching Markdown template in `templates/`; do not invent missing evidence, approvals or source data.
4. Run `scripts/validate.py` against rendered outputs; verify content and source traceability.
5. Return `templates/task-result.yaml` filled with artifact paths, evidence and errors.
6. Never edit the orchestrator Execution Plan, except the orchestrator itself.

## Modes
- Greenfield: new target design from requirements.
- Brownfield: reconstruct existing as-is and assess evidence confidence.
- Evolution: validate approved baseline, assess delta, design to-be and rollback.

## Capabilities
Topology, networking, sizing and FinOps

## Output templates
- `templates/topology-okf.md`
- `templates/capacity-okf.md`
- `templates/finops-okf.md`
