# Changelog — requirements-engineering

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

### Cambiado

- Adopción de STD-OKF-001 v1.9.0-stable; las salidas documentales de skills especialistas llevan tipo y metadatos OKF.


## [2.1.1] - 2026-11-08

### Corregido

- Los JSON operativos `evidence-register` y `source-inventory` se guardan en `.comsatel/requirements-engineering/runs/<run-id>/` y no en `requirements/`. El pathmap y el skill `af-evidence-context-designer` lo indican así.
- Referencias a la carpeta de ejecución escritas como `comsatel/` en lugar de `.comsatel/` (skills, README y pathmap).

## [2.1.0] - 2026-11-07

### Cambiado

- Propagación de STD-OKF-001 v1.8.0-stable (tipo `BSN`, ampliación aditiva): copia del estándar, referencias a la versión y lista de tipos aprobados de los validadores. Sin cambios de contrato de skills.

## [2.0.1] - 2026-11-07

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM`. El catálogo de términos es `business/terms/CTLG-TRM.md` (tipo `CTLG`), no `business/terms/index.md`. Corrección textual; sin cambios de contrato.

## [2.0.0] - 2026-11-07

Versión MAJOR: el cambio de formato de ID de User Stories es incompatible con 1.1.0 (ver la sección Cambiado). Incluye la ampliación EPC y la copia de STD-OKF-001 v1.7.0-stable.

### Añadido

- Tipo documental **EPC** (Épica): agrupa historias funcionalmente relacionadas del mismo RCP. ID `RCP-NNN-EPC-NNN`, en `requirements/context-packs/epics/`, plantilla `skills/af-user-story-designer/templates/epic.md`. Registrado en STD-OKF-001 v1.7.0-stable y propagado a las copias del plugin.
- G3 incluye las épicas: `workflow.py` declara `EPC` como salida de T02; el contrato, el checklist y el SKILL del orchestrator exigen que cada épica cite historias existentes, sin historias compartidas y con criterio de agrupación; `gate-evidence.json` de `af-user-story-designer` registra esas comprobaciones.
- `us_ids.py check` verifica que las US citadas por una épica existan y que ninguna pertenezca a dos épicas. `next` no cuenta las épicas.
- `validate_okf.py` acepta `EPC` en el catálogo aprobado y exige ID `RCP-NNN-EPC-NNN` y `related`.

### Cambiado

- **Incompatible (MAJOR):** el ID de cada User Story pasa a `RCP-NNN-US-NNN`, con `RCP-NNN` el Requirement Context Pack que origina la historia. Antes era `<PRODUCTO>-US-NNN`. El DSP no interviene en el ID porque se genera después de identificar las historias. El código de producto pasa a ser el metadato opcional `product`, fuera del ID.
- `scripts/us_ids.py next` recibe `--rcp RCP-NNN` en lugar de `--product` y numera por RCP. `check` valida el formato nuevo y sigue detectando duplicados entre archivos, KB y ramas.
- `validate_okf.py` exige `id` con `RCP-NNN-US-NNN` y hace opcional `product` (si se informa, en MAYÚSCULAS).
- Plantillas, SKILL, contratos, gate-checklists, `assets/pathmap.md`, README y VALIDATION actualizados al nuevo formato.
- Migración: las historias con `<PRODUCTO>-US-NNN` deben recibir un ID nuevo con `next --rcp`, conservar el anterior en `legacy_id`, renombrar el archivo y actualizar `related` y enlaces. Los issues de GitLab enlazados por `concept_id` requieren decisión humana antes de renumerar.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


### Cambiado

- **Endurecimiento (incompatible, D-21a):** `transition` (a `NEEDS_REVIEW`/`DONE`) y `approve-gate` exigen `--evidence` con un archivo existente dentro del workspace y guardan su ruta relativa; el texto libre se rechaza. Copias actualizadas en el SKILL del orquestador.
- `us_ids.py` solo recorre `requirements/` y acepta `--exclude <glob>` (repetible); copias de modelos o ejemplos fuera de esa carpeta ya no cuentan como historias duplicadas ni desplazan el siguiente ID (D-21b).
- README y SKILL del orquestador documentan que `brownfield` y `evolution` generan el mismo plan que `greenfield` y que la línea base depende de la revisión humana (D-21c).







## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [2.0.1] - 2026-10-29 (pre-línea base)

### Corregido

- Documentación y skills: el prefijo de la raíz de runs pasa de `comsatel/<plugin>/runs/` a `.comsatel/<plugin>/runs/`, como define `orchestrator_root` del pathmap (D-04).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [2.0.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/requirements-engineering/runs/<run-id>/` (campo `orchestrator_root` de `pathmap.json`, que los scripts leen en lugar de la ruta fija `comsatel/`). Las corridas existentes en `comsatel/` hay que migrarlas.

## [1.8.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [1.8.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador y los textos tratan `IMP` e `IMD` como aprobados.

## [1.7.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa. Se amplía el catálogo `PROPOSED` del validador con los 24 tipos nuevos.

## [1.6.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- El validador OKF reconoce `SOL` y `QAR` como tipos propuestos.
- La entrada de contexto reconoce el handoff de ideación (`SOL` y `handoff.json`) como una fuente más.

## [1.5.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

### Añadido
- IDs de User Stories globalmente únicos: formato `<PRODUCTO>-US-NNN`, ID inmutable y no reutilizable, ID previo (`HU-NN-NN`, `US-001`) en `legacy_id`. Nuevo `scripts/us_ids.py` (`next` y `check`, con `--also` para otras KB y `--git-ref` para ramas abiertas) y wrappers en `af-user-story-designer` y `af-requirements-pack-publisher`.

### Cambiado
- `validate_okf.py` rechaza una US cuyo `id` no sea `<product>-US-NNN` o sin `product` en mayúsculas.
- `af-user-story-designer`, `af-requirements-pack-publisher` y `af-requirements-orchestrator` exigen `us_ids.py check` en G3 y G6; plantilla, contrato, checklist y pathmap actualizados.
- Las US existentes con ID sin prefijo (por ejemplo `US-001` en `examples/testing`) dejan de validar hasta migrarlas: asignar ID nuevo, mover el anterior a `legacy_id` y renombrar el archivo.

## [1.5.0] - 2026-10-24 (pre-línea base)

### Añadido
- Entregable `DSP` (Development Scope Pack) como handoff de G6 (`af-requirements-pack-publisher`), en `requirements/scope-packs/DSP-NNN-<slug>.md`, con plantilla `development-scope-pack.md` basada en la KB piloto. Pathmap 1.5.0.

### Cambiado
- La salida `requirements-handoff` de G6 pasa a ser el `DSP`; `traceability-matrix` y `gate-report` siguen como evidencia sin sigla.

## [1.4.1] - 2026-10-24 (pre-línea base)

### Corregido
- Eliminadas las referencias colgantes a `templates/legacy/` y `references/legacy/` (retirados en el commit 9f580b0) en `MIGRATION-OKF.md`, `README.md`, `VALIDATION.md` y los `SKILL.md` y `technical-guidance.md` de los skills.
- Versiones de documentación alineadas: `VALIDATION.md` (v1.4.1), `VALIDATION-PATHS.md` y secciones «Mapeo obligatorio de rutas» de los `SKILL.md` (v1.4.0, igual que `assets/pathmap.md`).

## [1.4.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/requirements-engineering`.
