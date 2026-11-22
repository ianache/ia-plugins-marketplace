## [1.4.0] - 2026-11-21

### Cambiado

- Copia del estándar STD-OKF-001 propagada desde el maestro `v1.11.0-stable`: añade el tipo `IRP` (Informe o Reporte genérico) a la lista de tipos del validador; `QTD` pasa a cobertura, trazabilidad, TSN y TC, con estrategia y plan en `QTP`; incorpora la aclaración v1.9.0 sobre salidas de especialistas.

## [1.3.0] - 2026-11-07

### Cambiado

- Propagación de STD-OKF-001 v1.8.0-stable (tipo `BSN`, ampliación aditiva): copia del estándar, referencias a la versión y lista de tipos aprobados de los validadores. Sin cambios de contrato de skills.

## [1.2.1] - 2026-11-07

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM`. El catálogo de términos es `business/terms/CTLG-TRM.md` (tipo `CTLG`), no `business/terms/index.md`. Corrección textual; sin cambios de contrato.


## [1.2.0] - 2026-11-07

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md` (ampliación v1.7.0: tipo `EPC`, aprobado el 2026-11-07). Lista de tipos aprobados del validador regenerada desde la maestra. Sin cambios de contrato en los skills.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.

# Sin publicar
## Fixed
- README: encabezado con la versión de `plugin.json` (decía v3.1) (D-15).
- SKILL del orquestador: rutas con barras normales y prefijo `.comsatel/infra-architecture-design/runs/<run-id>/` (D-15).
- `assets/pathmap.json`: nuevo campo `okf_types` con la equivalencia slug → tipo OKF (`topology` → `ITP`, `baseline` → `IBL`…), verificada contra los catálogos y plantillas de cada skill; las claves existentes no cambian (D-15).

# v1.0.0 (2026-10-29)
## Changed
- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

# v6.0.0 (2026-10-29) (pre-línea base)
## Changed
- **Incompatible:** la raíz de estado operativo pasa a `.comsatel/infra-architecture-design/runs/` (`orchestrator_root` del pathmap; D-05). Los runs existentes en la ruta anterior (`.comsatel/comsatel-infrastructure/runs/`) deben moverse o reiniciarse. Textos, contratos, gates y pruebas actualizados.
# v5.0.0 (2026-10-27) (pre-línea base)
## Changed
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: se introduce `assets/pathmap.json` y `assets/pathmap.md` a nivel de plugin como única fuente y se eliminan los siete `skills/*/assets/pathmap.json`; el estado operativo pasa a `.comsatel/comsatel-infrastructure/runs/<run-id>/` (campo `orchestrator_root`, leído por `workflow.py`). Las corridas existentes en `comsatel/` hay que migrarlas.

# v4.2.0 (2026-10-27) (pre-línea base)
## Changed
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft.

# v4.1.0 (2026-10-26) (pre-línea base)
## Changed
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa.

# v4.0.0 (2026-10-25) (pre-línea base)
## Changed (incompatible)
- Los 22 documentos OKF dejan de usar el tipo provisional `DOC`: cada artefacto tiene su tipo propio en STD-OKF-001 v1.3.0-draft (20 tipos nuevos `IDS`, `IRQ`, `IBL`, `IIA`, `ITP`, `ICP`, `IFO`, `ISA`, `ICM`, `ITA`, `IOB`, `IRL`, `ISD`, `IAC`, `IDP`, `IRB`, `IAR`, `IHO`, `IXP`, `IXL`, `IGR`; el ADR reutiliza `ADR`). Los tipos siguen pendientes de aprobación corporativa.
- Las 22 plantillas definen secciones específicas por tipo con guía de contenido (antes compartían 5 secciones genéricas).
- `validate.py` (todos los skills) rechaza tipos fuera del catálogo y verifica las secciones mínimas del tipo.
- Copia del estándar sincronizada con el maestro `plugins/STD-OKF-001-v1.3.0-draft.md` (de 7 a 58 tipos propuestos).
## Added
- `assets/artifact-catalog.yaml`: mapa `types` artefacto → sigla.
- Pruebas: catálogo de tipos, secciones mínimas y rechazo de `DOC`.

# v3.1.0
## Fixed
- Command and agent files were single-line with literal backslash-n; frontmatter now parses.
- `validate.py` (all skills) looked for a literal backslash-n and rejected every rendered artifact; now parses real frontmatter.
- `workflow.py` wrote literal backslash-n to `*.events.jsonl`; the log is now valid JSONL.
- Literal backslash-n in README, legacy capability maps, ownership policy and SKILL.md template lists.
- INSTALL.md used a wrong plugin directory and command name.
## Changed
- Skill descriptions: the orchestrator is the user entry point; specialists are internal and dispatched only by the orchestrator.
- `workflow.py`: CLI (create, status, refresh, ready, update, submit-result, approve-gate); per-mode task graph and named gates loaded from `assets/dependency-map.yaml`; transitions loaded from `resources/state-machine.yaml`; task skills validated against `resources/skill-registry.yaml`.
- Gates are enforced: a task cannot become READY until its gates are APPROVED; gates require `human:<id>` and COMPLETED prerequisite tasks.
- `task-result.yaml` and output contracts aligned with the state machine (IN_REVIEW | BLOCKED | FAILED, sha256 evidence).

# v3.0.0
- Consolidated 10 specialists into six, retaining capability mapping.
- Self-contained skill assets, templates, scripts, resources and examples.
- Added local single-writer plan controller, event log, state transitions and human gate evidence.
- Five automated tests passed.

## Known limits
- No real Claude Code runtime invocation tested.
- Filesystem permission enforcement and concurrent process locking not implemented.
- OKF standard supplied is draft; DOC is a placeholder type and cannot be published as an approved corporate type.
- Templates require domain content validation and rendering before use.
