# Ejemplo de biz-knowledge-orchestrator

```text
python scripts/workflow.py init .comsatel/business-knowledge/runs/RUN-001 --scenario greenfield --workspace .
python scripts/workflow.py approve-gate .comsatel/business-knowledge/runs/RUN-001 --gate G0 --actor human:ana --evidence scope.md
python scripts/workflow.py transition .comsatel/business-knowledge/runs/RUN-001 --task T01 --to READY --actor agent --reason inicio
```

Bloqueo de ejemplo: aprobar G3 sin G2 aprobado => `ERROR: gate previo sin aprobar: G2`.
