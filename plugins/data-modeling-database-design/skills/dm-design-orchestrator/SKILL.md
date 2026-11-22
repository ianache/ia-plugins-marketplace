---
name: dm-design-orchestrator
description: Coordinar diseño de datos Greenfield, Brownfield y Evolution mediante plan DAG, tareas, evidencias y gates.
---
# dm-design-orchestrator

## Contrato de orquestación
1. Determinar escenario (`greenfield`, `brownfield`, `evolution`) y alcance autorizado.
2. Ejecutar `scripts/workflow.py init` para generar `.comsatel/data-modeling-database-design/runs/<run-id>/` y `design/database/<run-id>/`.
3. Completar fuentes y ADR en `scope-manifest.json`; solicitar aprobación humana de G0.
4. Asignar cada tarea a uno de los seis skills; respetar dependencias, validar outputs y registrar evidencias.
5. Gates con significado fijo: G1 reconstrucción As-Is; G2 ownership de datos; G3 modelo lógico; G4 modelo físico; G5 migración y compatibilidad; G6 validación y handoff. Cada escenario usa solo los que aplican y cada tarea entra por el gate de cierre de la anterior (G0 la primera):
   - `greenfield`: G2, G3, G4, G5 (migración inicial) y G6. No hay As-Is.
   - `brownfield`: G1, G2 y G6. Reconstruye y valida; no diseña To-Be ni migraciones.
   - `evolution`: G1 a G6.
6. Mantener separación de archivos operativos en `.comsatel/data-modeling-database-design/runs/<run-id>` y documentos conceptuales en `design/database/<run-id>`.
7. Publicar en KB mediante MR aprobado; entregar scripts de migración al repositorio de código según ADR; nunca hacer commit automático.

## Comandos
- `python scripts/workflow.py init --workspace . --run-id DEMO --scenario evolution`
- `python scripts/workflow.py check --workspace . --run-id DEMO`
- `python scripts/workflow.py status --workspace . --run-id DEMO`
- `python scripts/workflow.py approve-gate --workspace . --run-id DEMO --gate G0 --actor human:reviewer --evidence MR-123`
- `python scripts/workflow.py transition --workspace . --run-id DEMO --task T01 --to IN_PROGRESS --actor agent:dm --reason inicio`
- `python scripts/workflow.py transition --workspace . --run-id DEMO --task T01 --to NEEDS_REVIEW --actor agent:dm --reason entrega --evidence path/to/evidence`
- `python scripts/workflow.py complete --workspace . --run-id DEMO --task T01 --actor human:reviewer --evidence path/to/evidence`

## Estados de tarea
`PENDING` → `IN_PROGRESS` → `NEEDS_REVIEW` → `DONE`; `BLOCKED` y `FAILED` vuelven a `IN_PROGRESS`; `PENDING`, `IN_PROGRESS` y `NEEDS_REVIEW` pueden pasar a `BLOCKED`, y `IN_PROGRESS` y `NEEDS_REVIEW` a `FAILED`. Iniciar una tarea exige su gate de entrada aprobado y sus dependencias `DONE`; `NEEDS_REVIEW` y `DONE` exigen evidencia existente. `complete` pasa de `NEEDS_REVIEW` a `DONE`. Cada transición queda en `history` de `execution-plan.json`. Una corrida sin `schema_version` igual a la del CLI se rechaza: crear una nueva con `init`.

## Gates
La aprobación es una declaración registrada, no una verificación de identidad; integrar controles de GitLab antes de producción. Nunca autoaprobar. G6 requiere trazabilidad a FDT y fuentes, revisión de migraciones y rutas de handoff.
