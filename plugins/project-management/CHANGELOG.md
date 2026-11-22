# Changelog — project-management

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [2.1.0] - 2026-11-21

### Cambiado

- Plantilla `sprint-scope-pack.md`: el SSP declara `user_stories: [US-n, ...]` en el frontmatter, para que `qa-design` seleccione los TC del Sprint por historia.
- Adopción de STD-OKF-001 v1.9.0-stable; las salidas documentales de skills especialistas llevan tipo y metadatos OKF.


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

- `VALIDATION.md`: la cabecera indicaba v1.0.0 mientras la versión vigente es v1.1.0 (`.claude-plugin/plugin.json`). Restaura el test de documentación de rutas.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


### Cambiado

- Plantilla `CHG`: `approved_by` y `change_state` (proposed|approved|rejected|deferred) en el frontmatter; `status` se mantiene en el perfil de la KB (draft|stable|deprecated) y no toma el valor `approved`. SKILL y prueba `tests/test_chg_template.py` (D-27a).

### Cambiado

- **Endurecimiento (incompatible, D-17):** `workflow.py` valida la evidencia: `transition` a `NEEDS_REVIEW`/`DONE` exige un archivo existente y `approve-gate` un archivo existente o una referencia (URL o ID como `MR-12`). Antes aceptaba cualquier texto. Pruebas y ejemplos actualizados.

### Corregido

- Documentación: las referencias `comsatel/` restantes de los SKILL y `output-path-policy.md` pasan a `.comsatel/`; README y VALIDATION citan la versión de `plugin.json`, comprobado por `tests/test_rutas_docs.py` (D-17).







## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [2.0.1] - 2026-10-29 (pre-línea base)

### Corregido

- Documentación y skills: el prefijo de la raíz de runs pasa de `comsatel/<plugin>/runs/` a `.comsatel/<plugin>/runs/`, como define `orchestrator_root` del pathmap (D-04).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [2.0.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/project-management/runs/<run-id>/` (campo `orchestrator_root` de `pathmap.json`, que los scripts leen en lugar de la ruta fija `comsatel/`). Las corridas existentes en `comsatel/` hay que migrarlas.

## [1.4.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [1.4.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador y los textos tratan `PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG` y `CLS` como aprobados.

## [1.3.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa. Se amplía el catálogo `PROPOSED` del validador con los 24 tipos nuevos.

## [1.2.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- El validador OKF reconoce `SOL` y `QAR` como tipos propuestos.

## [1.1.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

## [1.1.0] - 2026-10-24 (pre-línea base)

### Añadido
- `gitlab_issues.py`: el issue de cada User Story replica el formato vigente en GitLab (verificado byte a byte contra el issue #9 de `cl2-flota/collaboration`): título `US{iid}: <título>`, fuente única de la historia, estimación de esfuerzo de referencia y trazabilidad completa. Opciones `--estimates` y `--project-issue-iid`; estimate nativo de GitLab en horas.
- Plantillas `templates/user-story-issue.md` y `templates/project-issue.md` en `mgt-work-publisher-synchronizer`: `gitlab_issues.py` las renderiza (los comentarios guía no se publican). Project Issue con Objetivo, Alcance, Exclusiones, Riesgos, Milestones y Trazabilidad; opción `--project-data` para riesgos y textos propios.
- Plantilla `templates/milestone-description.md`: la descripción del Milestone contiene solo los comandos `/project` … `/time_agent` (formato del Milestone 2 de kb-demo), sin texto libre. `gitlab_milestone.py` la renderiza y descarta lo que el SSP escriba después de la cabecera.
- Cada User Story tiene dos issues `Task` (plantillas `task-issue-dev.md` y `task-issue-qa.md`): `US{iid}: Coordinación del desarrollo con Superpowers` (label `Dev`) y `US{iid}: Coordinación del Aseguramiento de Calidad` (label `QA`), con tabla de contenido y las secciones Scope, Acceptance Criteria y Condition of Done, el mismo Milestone de la historia y enlace `relates_to` con ella. `gitlab_issues.py` los crea o completa sin duplicar.
- Estimate nativo de GitLab en la historia (horas de persona más agente de IA) y en cada tarea Dev y QA (su parte, también persona más agente), a partir de `estimate.py`; `estimate.py` expone `dev_agent_h`. `--estimates` acepta la salida del estimador.
- La plantilla `user-story-issue.md` incluye una tabla de costeo (Desarrollo, QA y Total) y una tabla con los dos issues `Task` de la historia; las tareas además quedan enlazadas con la historia en GitLab. La descripción de la historia se completa con los iid de las tareas cuando estas se crean después.
- Sección «Estimación y Costeo» en el Project Issue (antes de «Trazabilidad»): tabla por User Story del alcance con código, título, talla, # CA y horas de persona, de agente de IA y totales de QA y Dev, fila de totales y totales del Sprint a partir de `estimate.py`.
- Tipo `SSP` (Sprint Scope Pack) con plantilla basada en la KB piloto.

### Cambiado
- `SPL` (Iteration Plan) se reemplaza por `SSP` en `management/sprints/`. Cambio incompatible en un plugin aún sin publicar.
- El issue de User Story ya no copia los criterios de aceptación: viven solo en el archivo de la historia.
- Las historias se reconocen por la línea `- US: <ruta local>` (además del marcador `concept_id` de versiones previas).

## [1.0.0] - 2026-10-24

### Añadido
- Versión inicial: orchestrator y seis skills (acta y roadmap, backlog, publicación en GitLab, riesgos y cambios, avance, cierre).
