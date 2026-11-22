---
name: infrastructure-security-design
description: IAM, secrets, threat modeling and security controls. Internal specialist. Use only when dispatched by infrastructure-orchestrator with a task contract (task_id, execution_id, mode). For a user request to design or review infrastructure, use infrastructure-orchestrator instead.
---
# infrastructure-security-design

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
IAM, secrets, threat modeling and security controls

## Output templates
- `templates/security-architecture-okf.md`
- `templates/control-matrix-okf.md`
- `templates/threat-assessment-okf.md`
