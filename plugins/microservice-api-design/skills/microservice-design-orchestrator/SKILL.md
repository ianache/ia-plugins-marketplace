---
name: microservice-design-orchestrator
description: Planifica y gobierna Greenfield, Brownfield y Evolution de microservicios con reconstrucción As-Is, diseño To-Be, compatibilidad y handoff KB/codebase.
metadata:
  version: "0.1.0"
---
# Microservice Design Orchestrator

1. Identificar `scenario`: `greenfield`, `brownfield` (reconstrucción sin cambio) o `evolution`. Brownfield y Evolution pueden coexistir conceptualmente; en CLI `evolution` incluye reconstrucción As-Is. Registrar alcance, fuentes, repositorio, ref/commit, ADR y KB en `scope-manifest.yaml`.
2. Inicializar `python scripts/workflow.py init runs/<run-id> --scope <id> --scenario evolution --service <servicio> --workspace-root .`. Los tres escenarios requieren `codebase/<servicio>` (o `--codebase-service`); `init` valida antes de crear el run y un fallo no deja carpeta. Editar plan y validar DAG con `check`; obtener aprobación humana G0. Ningún skill puede aprobar su propio gate.
3. Delegar las seis especialidades solo cuando corresponda al escenario; usar `transition` para persistir progreso, outputs, evidencia y revisión. El motor no invoca Claude automáticamente.
4. Gates: G0 fuentes/alcance; G1 As-Is y límites; G2 arquitectura/contratos; G3 impacto y compatibilidad; G4 handoff y verificación. El gate de entrada de una tarea debe preceder al gate que esa tarea habilita.
5. Los skills especializados escriben exclusivamente en `design/microservices/<servicio>/` (el OpenAPI, en `codebase/<servicio>/`; según `assets/pathmap.json`); orchestrator en `runs/<run-id>/`. KB `codebase/<MICROSERVICIO>` se actualiza solo por MR autorizado. Código `src/main/resources/api/api.yaml` es ejemplo, no ruta obligatoria: resolver según ADR/repo.
6. El handoff debe distinguir `kb_target`, `repository`, `target_branch`, `source_ref`, `source_commit`, `artifacts[].source`, `artifacts[].target`, `action`, `validation`, `approval`. Ejecutar `validate-handoff` y pruebas contract-first externas antes de publicar. Nunca afirmar verificación de identidad por la CLI.
7. Validar Markdown conceptual con STD-OKF-001 v0.1.0-stable. Los documentos operativos YAML no son OKF. Mantener trazabilidad DDD→servicio→API/evento→KB→código→tests y registrar discrepancias sin sobrescrituras silenciosas.

8. Ejecutar `microservice-functionality-designer` después de contratos API/eventos y antes de Impact Analysis/Handoff. Producir `functionalities/fdt-manifest.yaml` y una FDT por capacidad dentro del alcance. `FUNCTIONALITY_DESIGN_READY` se materializa como control obligatorio al cerrar la tarea FDT en G2; sin FDT válidas no se permite DONE. Verificar referencias de QA/Data y no fabricar evidencias.
9. Publicar FDT aprobadas mediante MR en KB `codebase/<MICROSERVICIO>/docs/functionalities/`. El coding agent consume FDT + OpenAPI + ADR y escribe código en rutas verificadas.


## Output Pathmap obligatorio
- `workspace_root` es la raíz del proyecto/repositorio de trabajo (normalmente el directorio actual, `--workspace-root .`); `design/` cuelga directamente de ella y los documentos del servicio van en `design/microservices/<servicio>/...` (`init --service <servicio>`). Nunca usar `.comsatel/microservice-api-design/workspaces/<servicio>` ni otra subcarpeta de control como `workspace_root`: `init` lo rechaza.
- Leer el contrato de ejecución recibido del orchestrator. No elegir el directorio por cuenta propia.
- Usar `assets/pathmap.md` y `assets/pathmap.json` (raíz del plugin); validar con `scripts/validate_pathmap.py`.
- Escribir entregables especializados en la ruta asignada por el pathmap (`design/` o `codebase/<servicio>/`); reportar `document_type`, `output_path`, `pathmap_version` y evidencia de validación.
- Una ruta diferente solo procede por instrucción explícita del usuario y debe quedar registrada en el ledger.
- El orchestrator mantiene planes, gates y ledger bajo `.comsatel/microservice-api-design/runs/<run-id>/`.
- Los Markdown generados requieren frontmatter conforme a `STD-OKF-001 v0.1.0-stable`, sin inventar tipos documentales aprobados.

### Delegación obligatoria por pathmap
Antes de cada tarea leer `assets/pathmap.json`; enviar a cada skill un contrato con ruta absoluta resuelta. Rechazar entregables fuera de ruta, document types no mapeados y cambios de ruta no solicitados expresamente. No mezclar artefactos de control con arquitectura.
