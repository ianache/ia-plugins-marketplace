# Ejemplo de mgt-delivery-orchestrator

```text
python scripts/workflow.py init .comsatel/project-management/runs/2026-W43 --scenario cadence --workspace . --justification "ciclo semanal de riesgos e informe"
python scripts/workflow.py approve-gate .comsatel/project-management/runs/2026-W43 --gate G0 --actor human:ana --evidence scope.md
```

Bloqueo de ejemplo: aprobar G5 sin G4 aprobado => `ERROR: gate previo sin aprobar: G4`.
