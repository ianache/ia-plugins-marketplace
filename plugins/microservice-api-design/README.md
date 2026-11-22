# Microservice & API Design Plugin v1.2.1

6 skills + 1 orchestrator. Greenfield, Brownfield y Evolution. FDT por funcionalidad/capacidad, contrato OpenAPI/AsyncAPI, arquitectura hexagonal y handoff a KB/codebase.

## Cambios v0.3.0
- Nuevo `microservice-functionality-designer` y tipo FDT en STD-OKF-001 v1.2.0.
- `microservice-boundary-architecture-designer` consolida límites y arquitectura.
- Workflow agrega tarea FDT para los tres escenarios, entre contratos y evolución/handoff.
- Gate `FUNCTIONALITY_DESIGN_READY` ejecutable al marcar DONE la tarea FDT mediante validación del manifiesto y fichas.
- Plantillas con contrato por tipo documental (`ASIS`, `SVC`, `API`, `EVT`, `IMP`, `C4`, `FDT`, `HCB`), declaradas en `assets/pathmap.json` bajo `templates`.
- Publicación KB en `codebase/<MICROSERVICIO>/docs/functionalities/` solo por MR autorizado.

## Comandos
`python scripts/workflow.py init runs/demo --scope DSP-001 --scenario evolution --service <servicio> --workspace-root .`

Los tres escenarios requieren que exista `codebase/<servicio>` (o `--codebase-service <carpeta>`) porque escriben allí el OpenAPI (Greenfield y Evolution) y la vista C4 (todos); `init` valida esto antes de crear nada, de modo que un fallo no deja carpeta de run y el reintento con el mismo run-id es seguro.
`python scripts/workflow.py check runs/demo`
`python scripts/workflow.py validate-contract <contrato>.yaml`
`python scripts/workflow.py validate-handoff design/microservices/demo/handoff/codebase-handoff.yaml`
`python scripts/fdt_validate.py design/microservices/demo/functionalities/CL2-FDT-001-registrar-distribuidor.md`
`python scripts/fdt_validate.py design/microservices/demo/functionalities/fdt-manifest.yaml --manifest`

Requiere PyYAML. Validadores locales comprueban estructura, no semántica ni identidad del aprobador. La plantilla es ilustrativa y debe completarse antes de aprobación. No hay ejecución automática de Claude ni integración GitLab.

## Output Pathmap (pathmap version 0.7.0)
Los seis skills especializados escriben en `design/` o `codebase/<servicio>/` según `assets/pathmap.json`; el orchestrator en `.comsatel/microservice-api-design/runs/<run-id>/`. Los paths se resuelven desde `workspace_root`, que es la raíz del proyecto (`--workspace-root .`) y nunca una subcarpeta de `.comsatel/microservice-api-design/`. Los documentos del servicio quedan en `design/microservices/<servicio>/` (`init --service <servicio>`).
