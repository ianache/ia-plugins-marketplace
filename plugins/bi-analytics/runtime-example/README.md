# Runtime example

This blocked sample run demonstrates the canonical orchestrator layout:
`.comsatel/bi-analytics/runs/example-run/`.

- `plan.yaml`: run identity, mode, baseline and DAG.
- `plan-status.yaml`: authoritative planning and gate state.
- `tasks/<task-id>/task-status.yaml`: task state and evidence references.
- `evidence/<gate-id>/`: preserved gate evidence when available.
- `run-summary.md`: operational, non-OKF closure/pause summary.

Domain deliverables such as BIC, KPI, DSM, DMD, DSH and BIQ remain in `./bi/` according to the pathmap.
