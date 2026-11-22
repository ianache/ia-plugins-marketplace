---
name: infrastructure-orchestrator
description: Entry point for infrastructure architecture work. Use when the user asks to design, assess, review, migrate or evolve infrastructure (cloud, on-premise or hybrid, covering topology, networking, Kubernetes, security, observability, DR, IaC and CI/CD, costs) for a greenfield, brownfield or evolution initiative. Plans the workflow, dispatches the six specialist skills, validates results, enforces human gates and recovers.
metadata:
  version: "0.1.0"
---
# infrastructure-orchestrator

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
Workflow ownership, planning, dispatch, validation, gating and recovery

## Output templates
- `templates/execution-plan-okf.md`
- `templates/execution-log-okf.md`
- `templates/gate-register-okf.md`

## Storage layout (mandatory)
Every file the orchestrator owns lives under the base path `.comsatel/` (the `orchestrator_root` field of `assets/pathmap.json`), per STD-OKF-001 ("Ubicación y relación con el orchestrator"):

```
.comsatel/infra-architecture-design/runs/<run-id>/
    plan.json                    # authoritative plan (only workflow.py writes it)
    plan.json.events.jsonl       # event log
    task-results/                # task-result.yaml returned by each specialist
    execution-plan/  execution-log/  gate-register/   # rendered OKF documents
```

The plan, state, gates and operational evidence are not OKF conceptual documents and are never written under `knowledge/`. The CLI refuses plans outside this layout and task results outside the run folder. Specialist deliverables (topology, requirements, ADRs, ...) keep the paths of each skill's `assets/pathmap.json` and are published to the KB by Merge Request.

When dispatching a specialist, tell it to write its `task-result.yaml` to `<run>\task-results\<task_id>.task-result.yaml`.

## Plan engine
All plan mutations go through `scripts/workflow.py` (needs PyYAML). Use `--run-id` (and `--root` when the project root is not the current directory); `--plan` is accepted only for a path inside the layout above. The task graph per mode and the named gates live in `assets/dependency-map.yaml`; transitions live in `resources/state-machine.yaml`.

```
python scripts/workflow.py create --run-id <run-id> --mode greenfield|brownfield|evolution
python scripts/workflow.py status --run-id <run-id>
python scripts/workflow.py refresh --run-id <run-id>        # PENDING -> READY when dependencies are COMPLETED and required gates APPROVED
python scripts/workflow.py ready --run-id <run-id>          # tasks to dispatch
python scripts/workflow.py update --run-id <run-id> --task T1_assessment --to IN_PROGRESS --execution-id <id>
python scripts/workflow.py submit-result --run-id <run-id> --result <task-result.yaml>   # specialist result: IN_REVIEW | BLOCKED | FAILED
python scripts/workflow.py update --run-id <run-id> --task T1_assessment --to COMPLETED --execution-id <id> --use-submitted
python scripts/workflow.py approve-gate --run-id <run-id> --gate G1_BASELINE_APPROVED --actor human:<id> --evidence <ref>
```

Rules: a gate can only be approved by `human:<id>` after every task in its `after` list is COMPLETED; a task cannot become READY until its dependencies are COMPLETED and its `requires_gates` are APPROVED; a specialist never reports COMPLETED.

