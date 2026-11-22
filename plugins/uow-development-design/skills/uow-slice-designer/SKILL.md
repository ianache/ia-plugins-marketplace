---
name: uow-slice-designer
description: "Usar cuando un UCX aprobado deba partirse en una o más Unidades de Trabajo (slice vertical por US) que un solo developer con su agente pueda completar, con alcance, límites, dependencias, criterios cubiertos y dimensión."
metadata:
  version: "1.3.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Slice Designer
Parte una US en Unidades de Trabajo. **Slice vertical por US:** cada UOW atraviesa API, datos y lógica de un comportamiento completo y puede asignarse a un solo developer con su agente. Una US puede dar una o varias UOW.
## Required
`UCX` aprobado (`CONTEXT_GATE` PASS).
## Output
Una `UOW` por slice (plantilla `templates/UOW-OKF.md`) con: objetivo, alcance (qué incluye y qué excluye), criterios de aceptación cubiertos, dependencias (`depends_on_uow`), dimensión (horas de developer y de agente, si se estiman) y riesgos.
## Rules
- Todo criterio de aceptación del UCX queda cubierto por al menos una UOW y ninguna UOW cubre un criterio fuera de la US.
- Dividir cuando el slice no cabe en una asignación razonable o toca contextos de ownership distintos. No dividir por capa técnica.
- No definir contratos ni mapa de código: eso es de `uow-contract-binder` y `uow-codebase-mapper`.
- Las dependencias entre UOW forman un grafo sin ciclos.
## Verificación determinista
`python scripts/check_uow_package.py --root <dir> --profile slice` devuelve los checks `script` de `SLICE_GATE`. El orquestador expande el plan con las UOW del gate aprobado.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/SLICE_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T02.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/SLICE_GATE/` y es lo único que este skill escribe allí.

