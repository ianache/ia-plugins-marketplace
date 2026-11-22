# Changelog — data-modeling-database-design

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

## [2.1.0] - 2026-11-21

### Cambiado

- Copia del estándar STD-OKF-001 propagada desde el maestro `v1.11.0-stable`: añade el tipo `IRP` (Informe o Reporte genérico) a la lista de tipos del validador; `QTD` pasa a cobertura, trazabilidad, TSN y TC, con estrategia y plan en `QTP`; incorpora la aclaración v1.9.0 sobre salidas de especialistas.


### Cambiado

- Adopción de STD-OKF-001 v1.9.0-stable; las salidas documentales de skills especialistas llevan tipo y metadatos OKF.


### Corregido

- Versión citada en `README.md` (v1.2.1) y `DOCUMENTACION.md` (1.2.0) alineada con `plugin.json` (1.3.0), que es la fuente vigente. Corrección textual; sin cambios de contrato.

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




## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [0.8.0] - 2026-10-29 (pre-línea base)

### Añadido

- `scripts/validate_okf.py`, `scripts/validate_pathmap.py` y `scripts/validate.py` delgado en los 6 skills especialistas; los SKILL citan el comando (D-06).

### Cambiado

- **Incompatible:** la raíz de estado operativo pasa a `.comsatel/data-modeling-database-design/runs/` (`orchestrator_root` del pathmap; D-05). Los runs existentes en la ruta anterior (`runs/`) deben moverse o reiniciarse. Textos, contratos, gates y pruebas actualizados.

## [0.7.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Se introduce `assets/pathmap.json` (`deliverable_root`, `output_files`, `document_types`, `orchestrator_root`) y `assets/pathmap.md` con las reglas de ejecución; `workflow.py` lo lee. Sin cambio de rutas.

## [0.7.0] - 2026-10-27 (pre-línea base)

### Cambiado (incompatible)
- Las tareas tienen estados `PENDING`, `IN_PROGRESS`, `NEEDS_REVIEW`, `DONE`, `BLOCKED` y `FAILED`, con las transiciones permitidas y un historial en `execution-plan.json`. `complete` ahora exige `--actor` y pasa de `NEEDS_REVIEW` a `DONE` (antes pasaba directo desde `PENDING`).
- `execution-plan.json` lleva `schema_version`; el CLI rechaza las corridas sin ella o con otra versión.

### Añadido
- Comando `transition` (`--task`, `--to`, `--actor`, `--reason`, `--evidence`).
- Pruebas de transiciones, de gate de entrada y dependencias, y de rechazo de corridas con otra versión del esquema.

## [0.6.0] - 2026-10-27 (pre-línea base)

### Cambiado (incompatible)
- Greenfield deja de iniciar con la reconstrucción As-Is: ahora son 5 tareas (ownership, lógico, físico, migración inicial y validación).
- Los gates tienen significado fijo: G1 As-Is, G2 ownership, G3 lógico, G4 físico, G5 migración, G6 validación. Cada escenario usa solo los que aplican (Greenfield G2-G6, Brownfield G1, G2 y G6, Evolution G1-G6). Antes se numeraban según las tareas del escenario.
- `approve-gate` compara con el gate anterior que existe en el escenario, no solo con el número anterior.
- La migración se escribe en `migration/database-migration.md` (antes `evolution/`), también en Greenfield.
- `data-ownership.md` y `data-design-review.md` pasan a ser documentos auxiliares sin tipo OKF; los SKILL.md ya no sugieren `BC` ni `PDM` para ellos.

### Corregido
- Los SKILL.md citan `scope-manifest.json`, `execution-plan.json` y `gate-register.json`, que son los archivos que crea el CLI (antes `scope-manifest.yaml` y "task ledger").
- README alineado con la versión del plugin.

### Añadido
- `DOCUMENTACION.md` con skills, escenarios, gates, documentos y limitaciones.
- Pruebas de numeración fija de gates, de Greenfield sin As-Is y de orden de gates.

## [0.5.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft.

## [0.4.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa.

## [0.3.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.

## [0.2.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

## [0.2.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: tipos propuestos de Gestión (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`) y `IMD`/`TRM`; 36 tipos propuestos en total. Cambio aditivo y compatible.

## [0.1.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/data-modeling-database-design`.
