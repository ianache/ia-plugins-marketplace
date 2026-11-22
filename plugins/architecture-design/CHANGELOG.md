# Changelog — architecture-design

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

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

### Añadido

- Tipos `ACP`, `CFR`, `ADH` y `GOV` registrados en STD-OKF-001 (ampliación v1.4.0, aprobada el 2026-10-31) y reconocidos por `validate_okf.py`.
- ADR con sección visual obligatoria (de preferencia para todo ADR): diagrama Mermaid, catálogo de elementos con identificador `E-nn` y descripción, puntos de variación `VP-nn` con dimensión, variantes, momento de vinculación y responsable, y evaluación ATAM ligera (sensibilidad, compromiso, riesgo, no-riesgo) con escenarios `QA-nn` de seis partes.
- `scripts/validate_adr_body.py`: valida el cuerpo del ADR (secciones, cobertura entre diagrama y tablas, referencias, medidas de respuesta). `--render` comprueba que el Mermaid renderiza con `mmdc`; es solo local.
- `skills/architecture-asr-and-solution-designer/templates/okf-artifact.md`: tabla de árbol de utilidad con escenarios de seis partes, importancia y dificultad.
- Pruebas: `tests/test_adr_body.py` y fixture `tests/fixtures/adr-valid.md`.

### Corregido

- Las siete plantillas declaraban `type: ADR`. Ahora cada plantilla declara el tipo de su skill: `ASR`, `ACP`, `CFR`, `ADH` y `GOV`. `ADR` queda solo en `architecture-decision-governor`.
- `architecture-evolution-governor` deja de listar `ADR` como tipo preferente: el único productor de ADR es `architecture-decision-governor`.
- `architecture-conformance-assessor` y `architecture-evolution-governor` dejan de listar `RUN` como tipo preferente: pasan a `CFR` y `GOV`.
- `architecture-design-orchestrator` retira su plantilla OKF: no produce documentos conceptuales.

### Cambiado

- `architecture-decision-governor` es el único productor de ADR del plugin. `architecture-adr-writer` (skill personal) queda deprecado.
- Versión de los productores en plantillas: `1.1.0`.
- `DOCUMENTACION.md` y `README.md` alineados con la versión 1.1.0.
- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0 (DDR).

## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [2.0.1] - 2026-10-29 (pre-línea base)

### Corregido

- Documentación y skills: el prefijo de la raíz de runs pasa de `comsatel/<plugin>/runs/` a `.comsatel/<plugin>/runs/`, como define `orchestrator_root` del pathmap (D-04).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [2.0.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/architecture-design/runs/<run-id>/` (campo `orchestrator_root` de `pathmap.json`, que los scripts leen en lugar de la ruta fija `comsatel/`). Las corridas existentes en `comsatel/` hay que migrarlas.

## [1.5.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [1.5.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador acepta los tipos aprobados.

## [1.4.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa. Se amplía el catálogo `PROPOSED` del validador con los 24 tipos nuevos.

## [1.3.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- El validador OKF reconoce `SOL` y `QAR` como tipos propuestos.

## [1.2.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

## [1.2.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: tipos propuestos de Gestión (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`) y `IMD`/`TRM`; 36 tipos propuestos en total. Cambio aditivo y compatible.
- El validador OKF reconoce los tipos propuestos de Gestión; los acepta hasta el nivel de perfil y los rechaza en publicación, como el resto de tipos propuestos.

## [1.1.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/architecture-design`.
