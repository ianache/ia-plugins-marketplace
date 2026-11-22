---
name: uow-codebase-mapper
description: "Usar cuando una UOW deba aterrizarse en un repositorio: referencia base, rutas permitidas, zonas prohibidas, ADR y convenciones aplicables, y análisis del código existente en Brownfield y Evolution."
metadata:
  version: "1.3.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Codebase Mapper
Aterriza la UOW en un repositorio y fija los límites de escritura del agente.
## Required
`UOW` aprobada y, si existe, el `HCB` del servicio y los ADR (la ruta de código se resuelve por ADR y repositorio, nunca por convención universal).
## Output
`UCM` (plantilla `templates/UCM-OKF.md`): `repository` (`project`, `target_branch`, `source_ref`, `source_commit`, mismo bloque que `HCB`), `allowed_paths`, `forbidden_paths`, `adr_refs`, convenciones, `existing_code_analysis` y orden de migraciones.
## Rules
- `GREENFIELD`: proponer la estructura destino a partir de ADR y convenciones; no hay código que analizar.
- `BROWNFIELD` y `EVOLUTION`: analizar el código existente de la zona a tocar (puntos de extensión, pruebas existentes, riesgos de regresión) y marcarlo `performed: true` con evidencia. En Evolution, registrar compatibilidad hacia atrás y rollback: campos `backward_compatibility` (`assessed: true`, `summary`) y `rollback` (`defined: true`, `summary`) y las secciones `## Compatibilidad hacia atrás` y `## Rollback` con contenido; el check `compat-and-rollback-present` (script) de `CODEBASE_GATE` lo verifica.
- El commit base debe ser real; no se acepta `HEAD` ni marcadores.
- Declarar zonas prohibidas (código compartido, otros servicios, configuración de despliegue) aunque el agente tenga acceso técnico.
## Verificación determinista
`python scripts/check_uow_package.py --root <dir> --profile codebase --uow UOW-001` devuelve los checks `script` de `CODEBASE_GATE`.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/CODEBASE_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T04.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/CODEBASE_GATE/` y es lo único que este skill escribe allí.

