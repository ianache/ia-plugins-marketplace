# Microservice & API Design — Documentación del plugin

Plugin de Claude Code que diseña microservicios y sus APIs en tres escenarios (Greenfield, Brownfield y Evolution): reconstrucción As-Is, límites y arquitectura hexagonal To-Be, contratos OpenAPI/AsyncAPI, fichas de diseño por funcionalidad (FDT), análisis de impacto y handoff a la KB y al código. Usa **un orquestador y seis skills especialistas**, con gates de aprobación humana.

- **Versión:** 1.2.0 (pathmap 0.7.0) · **Documentos:** STD-OKF-001 v1.11.0-stable
- **Invocación:** `/microservice-api-design:microservice-design-orchestrator`
- **Entrada:** DDD aprobado (`BC`, `CTX`, `AGG`, `VO`, `EVT`), ADR, DSP/SSP, KB `codebase/<MICROSERVICIO>` y repositorios.

---

## 1. Skills

| Skill | Qué hace | Entregable |
| :--- | :--- | :--- |
| `microservice-design-orchestrator` | Identifica el escenario, planifica el DAG, controla gates y persiste el progreso. No invoca a Claude automáticamente. | Registros del run |
| `microservice-reconstruction-analyzer` | Reconstrucción As-Is: repositorio, rutas reales, OpenAPI, código, dependencias, persistencia, eventos y tests. Cita archivo y commit por afirmación. | `architecture-reconstruction.md` |
| `microservice-boundary-architecture-designer` | Límites de servicios y arquitectura hexagonal To-Be: responsabilidades, ownership, adaptadores, puertos, C4 y NFR. | `service-boundaries.md`, `service-architecture.md` |
| `api-integration-contract-designer` | Contract First: OpenAPI 3.1, AsyncAPI/eventos y gRPC si aplica. Distingue Domain Events de Integration Events y analiza compatibilidad. | `api-integration-design.md` |
| `microservice-functionality-designer` | Una FDT por capacidad: entradas, salidas, errores, reglas, datos, seguridad, secuencias, pruebas y handoff. | `fdt-manifest.yaml` + una FDT por funcionalidad |
| `microservice-evolution-planner` | Compara As-Is y To-Be: breaking changes, consumidores, migraciones, rollout, rollback y riesgos. En Greenfield justifica N/A. | `impact-analysis.md` |
| `microservice-codebase-handoff` | Mapea la KB `codebase/<MICROSERVICIO>` al repositorio de código. Resuelve rutas por ADR y evidencia. | `codebase-handoff.yaml` |

Reglas comunes:

- No inventar fuentes ausentes ni evidencias. Declarar la incertidumbre.
- Un bounded context no equivale obligatoriamente a un microservicio. No se redefine el DDD aprobado.
- Ningún skill aprueba su propio gate. No hay push ni Merge Request sin autorización explícita.
- Los validadores locales comprueban estructura, no semántica ni identidad del aprobador.

---

## 2. Secuencia por escenario

Cada tarea tiene un **gate de entrada**: debe estar aprobado para iniciarla. Aprobar el gate siguiente exige que todas las tareas con el gate anterior como entrada estén en `DONE`.

### Greenfield

| Tarea | Skill | Depende de | Gate de entrada |
| :-: | :--- | :--- | :-: |
| T01 | boundary-architecture-designer (límites) | — | G0 |
| T02 | boundary-architecture-designer (arquitectura To-Be) | T01 | G0 |
| T03 | api-integration-contract-designer | T02 | G1 |
| T03F | functionality-designer (FDT) | T03 | G2 |
| T04 | evolution-planner (N/A documentado) | T03F | G2 |
| T05 | codebase-handoff | T04 | G3 |

### Brownfield (reconstrucción sin cambio)

| Tarea | Skill | Depende de | Gate de entrada |
| :-: | :--- | :--- | :-: |
| T01 | reconstruction-analyzer (As-Is) | — | G0 |
| T02 | boundary-architecture-designer (conciliación de límites) | T01 | G0 |
| T03 | boundary-architecture-designer (evaluación de arquitectura) | T02 | G1 |
| T04 | api-integration-contract-designer (inventario) | T03 | G1 |
| T04F | functionality-designer (FDT) | T04 | G2 |
| T05 | evolution-planner (impacto solo documental) | T04F | G2 |
| T06 | codebase-handoff (conciliación KB/código) | T05 | G3 |

### Evolution

| Tarea | Skill | Depende de | Gate de entrada |
| :-: | :--- | :--- | :-: |
| T01 | reconstruction-analyzer (As-Is) | — | G0 |
| T02 | boundary-architecture-designer (evolución de límites) | T01 | G0 |
| T03 | boundary-architecture-designer (To-Be) | T02 | G1 |
| T04 | api-integration-contract-designer (evolución) | T03 | G1 |
| T04F | functionality-designer (FDT) | T04 | G2 |
| T05 | evolution-planner (impacto y migración) | T04F | G2 |
| T06 | codebase-handoff | T05 | G3 |

Estados de tarea: `PENDING`, `READY`, `IN_PROGRESS`, `NEEDS_REVIEW`, `DONE`, `BLOCKED`, `FAILED`. Una tarea llega a `DONE` solo desde `NEEDS_REVIEW`, con evidencia y con sus salidas existentes.

---

## 3. Entregables

### 3.1 Familias documentales (pathmap v0.7.0)

| Sigla | Nombre | Lo produce | Carpeta en el workspace |
| :-: | :--- | :--- | :--- |
| `ASIS` | As-Is Architecture Reconstruction | reconstruction-analyzer | `design/microservices/<servicio>/as-is/` |
| `SVC` | Service Design Specification | boundary-architecture-designer | `design/microservices/<servicio>/` |
| `API` | Contratos de API e integración | api-integration-contract-designer | `design/microservices/<servicio>/` |
| `EVT` | Contratos de eventos | api-integration-contract-designer | `design/microservices/<servicio>/events/` |
| `C4` | Vista de arquitectura C4 | boundary-architecture-designer | `codebase/<servicio>/docs/` |
| `FDT` | Ficha de Diseño Técnico de Funcionalidad | functionality-designer | `design/microservices/<servicio>/functionalities/` |
| `IMP` | Impact and Evolution Analysis | evolution-planner | `design/microservices/<servicio>/evolution/` |
| `HCB` | Codebase Handoff Contract | codebase-handoff | `design/microservices/<servicio>/handoff/` |

`ASIS`, `SVC`, `IMP` y `HCB` están aprobadas en STD-OKF-001 v1.11.0-stable. `FDT` sí es tipo oficial desde v1.2.0. Un tipo sin mapeo queda bloqueado.

### 3.2 Archivos del workflow

Rutas relativas a `design/microservices/<servicio>/` (la clave `to-be/...` del pathmap es solo el identificador de lookup; no existe carpeta `to-be/`).

| Archivo | Familia | Skill |
| :--- | :-: | :--- |
| `as-is/architecture-reconstruction.md` | `ASIS` | reconstruction-analyzer |
| `service-boundaries.md` | `SVC` | boundary-architecture-designer |
| `service-architecture.md` | `SVC` | boundary-architecture-designer |
| `api-integration-design.md` | `API` | api-integration-contract-designer |
| `events/event-contracts.md` | `EVT` | api-integration-contract-designer |
| `c4-architecture.md` (en `codebase/<servicio>/docs/`, no bajo `design/`) | `C4` | boundary-architecture-designer |
| `functionalities/fdt-manifest.yaml` y `functionalities/<FDT-ID>-<slug>.md` | `FDT` | functionality-designer |
| `evolution/impact-analysis.md` | `IMP` | evolution-planner |
| `handoff/codebase-handoff.yaml` | `HCB` | codebase-handoff |

La publicación de las FDT aprobadas a la KB `codebase/<MICROSERVICIO>/docs/functionalities/` se hace solo por Merge Request autorizado.

### 3.3 Registros del orquestador

En `.comsatel/microservice-api-design/runs/<run-id>/`: `execution-plan.yaml`, `task-ledger.yaml`, `gate-register.yaml`, `scope-manifest.yaml` y `run-status.md`.

---

## 4. Gates

| Código | Significado | Se aprueba cuando |
| :-: | :--- | :--- |
| `G0` | **Fuentes y alcance:** plan, fuentes, repositorio, ref/commit, ADR y KB definidos. | `scope-manifest.yaml` con fuentes y sin `missing_sources`. |
| `G1` | **As-Is y límites:** reconstrucción y límites de servicio aceptados (en Greenfield, límites y arquitectura). | Tareas con entrada G0 en `DONE` y G0 aprobado. |
| `G2` | **Arquitectura y contratos:** arquitectura To-Be y contratos de API/eventos aceptados. | Tareas con entrada G1 en `DONE` y G1 aprobado. |
| `G3` | **Impacto y compatibilidad:** FDT, análisis de impacto y migración aceptados. | Tareas con entrada G2 en `DONE` y G2 aprobado. |
| `G4` | **Handoff y verificación:** handoff a KB y codebase validado y listo para publicar. | Tareas con entrada G3 en `DONE`, G3 aprobado y `codebase-handoff.yaml` válido. |

Estados de un gate: `NOT_READY`, `PENDING_APPROVAL`, `APPROVED`, `REJECTED`. Aprobar exige actor y evidencia, y el actor es una declaración que el CLI no autentica.

### Control FUNCTIONALITY_DESIGN_READY

Control obligatorio al cerrar la tarea FDT, dentro del tramo de G2 a G3. No es un gate G*:

- Cada funcionalidad del alcance tiene su FDT.
- Sin referencias obligatorias sin resolver y con `operationId` de OpenAPI alineado.
- Fuentes y escenarios verificables.
- Aprobación humana para publicar.

El CLI ejecuta `fdt_validate` sobre el manifiesto al pasar la tarea a `DONE`. Sin FDT válidas no se permite `DONE`.

### Control de G4

Antes de aprobar G4, el CLI ejecuta `validate-handoff`. Exige `service_id`, `scenario`, `knowledge_base.target` bajo `codebase/`, repositorio con `project`, `target_branch`, `source_ref` y `source_commit`, referencias a ADR, artefactos con `source`, `target`, `action` y `validation`, y `require_human_approval: true`. Rechaza rutas absolutas o con `..`.

---

## 5. Uso

```bash
python scripts/workflow.py init <run> --scope DSP-001 --scenario evolution --service <servicio> --workspace-root <workspace>
python scripts/workflow.py check <run>
python scripts/workflow.py approve-gate <run> --gate G0 --actor 'human:<aprobador>' --evidence '<referencia>'
python scripts/workflow.py transition <run> --task T01 --to READY --actor orchestrator --reason 'G0 aprobado'
python scripts/workflow.py status <run>
python scripts/workflow.py validate-contract <contrato>.yaml
python scripts/workflow.py validate-handoff <codebase-handoff>.yaml
python scripts/fdt_validate.py <FDT>.md
python scripts/fdt_validate.py <fdt-manifest>.yaml --manifest
```

Greenfield y Evolution requieren que exista `codebase/<servicio>` (o `--codebase-service <carpeta>`) porque escriben el OpenAPI allí; `init` valida esto antes de crear nada, de modo que un fallo no deja carpeta de run y el reintento con el mismo run-id es seguro.

Requiere PyYAML. No hay ejecución automática de Claude ni integración con GitLab.

---

## 6. Observaciones detectadas al documentar

1. **Resuelto:** se copió `STD-OKF-001-v1.11.0-stable.md` a `standards/` desde otro plugin (copia idéntica en cinco plugins).
2. **Resuelto:** versiones alineadas con `plugin.json`; el pathmap tiene su propia versión (`pathmap.json` → `version`).
3. **Resuelto:** el `README.md` usa `--workspace-root` y documenta `validate-contract` y `validate-handoff`.
4. **Resuelto:** `tests/test_smoke.py` se actualizó a la versión 0.4.0, a `--workspace-root` y a las FDT del manifiesto.
5. **Resuelto:** `C4` y `EVT` tienen tarea propia en los tres escenarios (`docs/c4-architecture.md` → `codebase/<servicio>/docs/`; `events/event-contracts.md`). Por el C4, Brownfield también requiere `codebase/<servicio>`.
6. **Gates distintos por escenario.** El mismo código cubre trabajo diferente según el escenario. Por ejemplo, G1 es "As-Is y límites" en Brownfield y Evolution, pero en Greenfield cubre límites y arquitectura.
7. **Resuelto:** la familia de rutas `HOF` colisionaba con el tipo aprobado `HOF` (UX/UI Development Handoff Contract) de STD-OKF-001 v1.11.0-stable. Se renombró a `HCB` en el pathmap y en las políticas de rutas.
8. **Compatibilidad con v1.3.0 verificada.** v1.3.0 es aditiva: agrega ocho tipos de UX/UI, Web y Mobile y no cambia el perfil de `FDT` ni las reglas de metadatos. `okf_validate.py` y `fdt_validate.py` aplican las reglas vigentes de ambas versiones, y `templates/fdt-functionality.md` pasa los dos validadores. El docstring de `okf_validate.py` ya lo indica.

## Contrato OpenAPI y C4 en el codebase
- OpenAPI: `codebase/<servicio>/src/main/resources/api.yaml`; si existe `codebase/<servicio>/api/`, `codebase/<servicio>/api/src/main/resources/api.yaml`. Aplica a Greenfield y Evolution (Brownfield solo inventaría). El diseño (`api-integration-design.md`) va en `design/microservices/<servicio>/`.
- C4: siempre en `codebase/<servicio>/docs/`.
- Si `codebase/<servicio>` no existe (o el nombre difiere), **solicitar al humano** la carpeta del servicio dentro de `codebase/` y pasarla con `init --codebase-service <carpeta>`. No inventar la ruta.
