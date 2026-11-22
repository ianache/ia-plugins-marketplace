---
name: infrastructure-delivery-design
description: IaC, Terraform, Helm, CI/CD, GitOps, deployment and rollback. Internal specialist. Use only when dispatched by infrastructure-orchestrator with a task contract (task_id, execution_id, mode). For a user request to design or review infrastructure, use infrastructure-orchestrator instead.
metadata:
  version: "0.1.0"
---
# infrastructure-delivery-design

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
IaC, Terraform, Helm, CI/CD, GitOps, deployment and rollback

## Output templates
- `templates/iac-specification-okf.md`
- `templates/deployment-plan-okf.md`
- `templates/rollback-plan-okf.md`
