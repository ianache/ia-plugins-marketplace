---
name: uow-contract-binder
description: "Usar cuando una UOW deba enlazarse con las operaciones API y los objetos de datos exactos (tablas, migraciones) que debe implementar, verificando que los contratos existen, están versionados y son coherentes entre API y BD, sin inventar nada."
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Contract Binder
Enlaza una UOW con los contratos que debe implementar o consumir. **Solo enlaza lo que existe**.
## Required
`UOW` aprobada (T02 PASS) y el `UCX`.
## Output
`UCB` (plantilla `templates/UCB-OKF.md`): `api_operations` (operationId, método, ruta, contrato y versión, FDT), `data_objects` (tablas, migraciones y versión), `api_fields` y `mapping` API→columna (con transformación y nulabilidad, o `na_reason`), eventos y brechas.
## Rules
- Un contrato, operación, campo o tabla que no existe en las fuentes es una **brecha**, no algo a inventar: se registra y se escala (puede requerir un cambio en el diseño de API o de BD).
- Fijar la versión de cada contrato; `latest` no es una versión.
- Verificar coherencia API↔BD: cada campo API tiene columna o un motivo explícito.
- Si la UOW no usa API o no toca datos, declarar `api_not_applicable` o `data_not_applicable` con motivo.
## Verificación determinista
`python scripts/check_uow_package.py --root <dir> --profile binding --uow UOW-001` devuelve los checks `script` de `BINDING_GATE`.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/BINDING_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T03.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/BINDING_GATE/` y es lo único que este skill escribe allí.

