# Changelog — microservice-api-design

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

## [1.5.0] - 2026-11-21

### Cambiado

- Copia del estándar STD-OKF-001 propagada desde el maestro `v1.11.0-stable`: añade el tipo `IRP` (Informe o Reporte genérico) a la lista de tipos del validador; `QTD` pasa a cobertura, trazabilidad, TSN y TC, con estrategia y plan en `QTP`; incorpora la aclaración v1.9.0 sobre salidas de especialistas.


## [1.4.0] - 2026-11-08

### Añadido

- Plantillas con contrato para `ASIS` (`asis-reconstruction.md`), `SVC` (`service-boundaries.md` y `service-architecture.md`), `API` (`api-integration-design.md`), `EVT` (`event-contracts.md`), `IMP` (`impact-analysis.md`) y `C4` (`c4-architecture.md`): frontmatter del tipo, secciones obligatorias y reglas de validación.
- `assets/pathmap.json`: sección `templates` que declara la plantilla de cada tipo documental.
- Pruebas `tests/test_templates.py`: cada tipo de salida tiene plantilla, la plantilla declara su tipo, tiene las secciones obligatorias y no contiene datos reales.

### Cambiado

- `codebase-handoff.yaml` (`HCB`): plantilla de contrato con marcadores `<<...>>` y campos obligatorios, en lugar de un ejemplo con datos de un servicio real.
- `api-integration-contract-designer`: el diseño de API se escribe en `design/microservices/<servicio>/to-be/api-integration-design.md`, según el pathmap.
- `README.md`: lista las plantillas por tipo.

### Eliminado

- `templates/service-design-contract.yaml`: no estaba en el pathmap ni lo usaba ningún skill; sustituido por las plantillas `SVC`.

### Corregido

- Referencias a la carpeta de ejecución escritas como `comsatel/` en lugar de `.comsatel/`.

## [1.3.0] - 2026-11-07

### Cambiado

- Propagación de STD-OKF-001 v1.8.0-stable (tipo `BSN`, ampliación aditiva): copia del estándar, referencias a la versión y lista de tipos aprobados de los validadores. Sin cambios de contrato de skills.

## [1.2.1] - 2026-11-07

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM`. El catálogo de términos es `business/terms/CTLG-TRM.md` (tipo `CTLG`), no `business/terms/index.md`. Corrección textual; sin cambios de contrato.

## [1.2.0] - 2026-11-07

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md` (ampliación v1.7.0: tipo `EPC`, aprobado el 2026-11-07). Lista de tipos aprobados del validador regenerada desde la maestra. Sin cambios de contrato en los skills.

### Corregido

- `scripts/okf_validate.py`: la comprobación de tipos usaba `TYPES`, no definida, y provocaba `NameError` en la validación de perfil; ahora usa la lista `APPROVED`. Restaura los tests de `workflow.py` (escenarios greenfield, brownfield y evolution).

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [0.10.0] - 2026-10-29 (pre-línea base)

### Añadido

- Tareas propias para `EVT` (`events/event-contracts.md`, skill api-integration-contract-designer) y `C4` (`docs/c4-architecture.md` en `codebase/<servicio>/docs/`, skill boundary-architecture-designer) en Greenfield, Brownfield y Evolution; FDT depende de ambas. `pathmap.json` 0.7.0 (D-10).

### Cambiado

- **Incompatible:** `approve-gate` exige `--actor human:<nombre>`; antes aceptaba cualquier texto (D-07).
- Brownfield también requiere `codebase/<servicio>` (por la vista C4).
- Los SKILL y DOCUMENTACION citan las rutas reales `design/microservices/<servicio>/<archivo>` (sin carpeta `to-be/`) y se eliminó el artefacto de plantilla `design/ (ruta exacta según ...)` (D-03).

### Corregido

- `workflow.py init` es atómico: valida `codebase/<servicio>` antes de crear la carpeta del run y `design/`; un fallo ya no deja residuos ni bloquea el reintento con el mismo run-id (D-02).
- Documentado en README, DOCUMENTACION y SKILL del orquestador que Greenfield y Evolution requieren `codebase/<servicio>` o `--codebase-service` (D-02).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [0.9.0] - 2026-10-27 (pre-línea base)

### Cambiado (incompatible)
- Los documentos de microservicio se ubican por servicio: `design/microservices/<servicio>/{as-is,services,functionalities,evolution,handoff}/` (antes `architecture/microservices/<tipo>/`); `EVT` pasa a `design/microservices/<servicio>/events/` y los registros del orchestrator a `.comsatel/microservice-api-design/runs/`. `pathmap.json` pasa a 0.5.0 con el marcador `{service}`; `validate_pathmap.py` exige un id de servicio válido y lo infiere de la ruta al validar. `workflow.py init` requiere `--service <servicio>` y lo guarda como `service` en `execution-plan.yaml`. `API` pasa a `design/microservices/<servicio>/` (evita que un servicio sobrescriba a otro); `C4` va siempre en `codebase/<servicio>/docs/`.
- El contrato OpenAPI (Greenfield/Evolution) se escribe en `codebase/<servicio>/src/main/resources/api.yaml`, o en `codebase/<servicio>/api/src/main/resources/api.yaml` si existe esa carpeta. Si `codebase/<servicio>` no existe, `init` falla pidiendo al humano la carpeta (`--codebase-service`) y sugiere nombres similares. `pathmap.json` 0.6.0.

- `assets/pathmap.md` queda solo con las reglas de ejecución y remite a `pathmap.json` para el mapeo; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace a ambos, sin contenido duplicado.

### Corregido
- En Brownfield los documentos quedaban en `.comsatel/microservice-api-design/workspaces/<servicio>/architecture/...` porque `workspace_root` no estaba definido y el agente lo inventaba. Ahora `workspace_root` es la raíz del proyecto, `init` rechaza uno dentro de `.comsatel/microservice-api-design/` y el SKILL del orchestrator y el README lo explicitan.

## [0.8.0] - 2026-10-27 (pre-línea base)

### Corregido
- `tests/test_smoke.py` ya no exige una versión fija (`0.4.0`): comprueba que `plugin.json` sea SemVer y coincida con la última versión del CHANGELOG. Sin cambio de contrato.

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador acepta los tipos aprobados y la documentación cita v1.3.0-stable.

## [0.7.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa. Se amplía el catálogo `PROPOSED` del validador con los 24 tipos nuevos.

## [0.6.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- El validador OKF reconoce `SOL` y `QAR` como tipos propuestos.

## [0.5.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

## [0.5.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: tipos propuestos de Gestión (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`) y `IMD`/`TRM`; 36 tipos propuestos en total. Cambio aditivo y compatible.
- El validador OKF reconoce los tipos propuestos de Gestión; los acepta hasta el nivel de perfil y los rechaza en publicación, como el resto de tipos propuestos.

## [0.4.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/microservice-api-design`.
