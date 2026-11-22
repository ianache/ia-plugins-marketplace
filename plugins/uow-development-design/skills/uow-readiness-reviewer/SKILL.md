---
name: uow-readiness-reviewer
description: "Usar como revisor independiente del paquete de una UOW antes de asignarla: completitud, trazabilidad, ausencia de alcance inventado y preguntas abiertas, sin rediseñar el paquete."
metadata:
  version: "1.3.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Readiness Reviewer
Revisión independiente del paquete antes de asignar la UOW. **No puede ser el autor** de ningún documento del paquete (check `reviewer-independent-of-author`).
## Required
`UOW`, `UCB`, `UCM` y `UAP` con sus gates en PASS, y el `UCX`.
## Output
`UWR` (plantilla `templates/UWR-OKF.md`): hallazgos con severidad, alcance inventado, preguntas abiertas y `recommendation` (`READY_FOR_APPROVAL`, `NEEDS_REWORK` o `BLOCKED`). Es una propuesta: la aprobación es humana (`UOW_READY_GATE`).
## Checks
Completitud del paquete, trazabilidad `US → UOW → UCB/UCM/UAP`, criterios cubiertos, contratos fijados, límites de código, plan verificable, preguntas bloqueantes abiertas y alcance que no sale de la US ni del DSP.
`python scripts/check_uow_package.py --root <dir> --profile readiness --uow UOW-001` ejecuta los checks `script` del gate.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/READINESS_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T06.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/READINESS_GATE/` y es lo único que este skill escribe allí.

