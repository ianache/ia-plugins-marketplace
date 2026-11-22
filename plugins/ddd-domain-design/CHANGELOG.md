# Changelog — ddd-domain-design

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

## [2.2.0] - 2026-11-21

### Cambiado

- Las plantillas de salida viven en `skills/<skill>/templates/` del skill que produce el documento. Se movieron `execution-plan.yaml`, `task-ledger.yaml` y `gate-register.yaml` a `skills/ddd-design-orchestrator/templates/`.
- `task-result.yaml` (registro operativo, idéntico en los siete skills) se mueve a `skills/ddd-design-orchestrator/templates/`: los registros de control del flujo los mantiene el orquestador. La raíz del plugin no tiene `templates/`.
- `ddd-domain-event-designer`: `templates/evt-okf.md` añade las secciones «Clasificación del evento», «Ownership», «Semántica y versionado», «Preguntas abiertas» y «Trazabilidad» para cubrir lo que el skill exige (comandos, eventos de dominio vs. integración, ownership, semántica y versionado).
- Pruebas: `tests/test_templates.py` comprueba la carpeta de cada skill, que no exista `templates/` en la raíz y que los registros operativos estén en la carpeta del orquestador.

### Eliminado

- Copias de `task-result.yaml` en cada skill, y las copias en la raíz de las plantillas de cada skill; `domain-discovery-aux.md` (marcador de obsolescencia) y `acp-okf.md` (variante de ejemplo sin skill que la referencie).
- Referencias «copia idéntica en templates/ de la raíz» en los `SKILL.md`.

## [2.1.2] - 2026-11-21

### Cambiado

- `ddd-tactical-model-designer`: añade «Plantilla de salida». El catálogo `tactical-model.md` se genera con `templates/ctlg-agg-okf.md` (`type: CTLG`, `indexes: AGG`), cada aggregate con `templates/agg-okf.md` y cada value object con `templates/vo-okf.md`.
- `ddd-domain-event-designer`: añade «Plantilla de salida». El catálogo `domain-events.md` se genera con `templates/ctlg-evt-okf.md` (`type: CTLG`, `indexes: EVT`) y cada evento con `templates/evt-okf.md`.
- `ddd-domain-contract-validator`: añade «Plantilla de salida». `CFR-domain-validation.md` se genera con `templates/cfr-okf.md` (`type: CFR`) y el contrato con `templates/domain-design-contract.yaml`.
- Las plantillas de documento (T01 a T06) se copian a la carpeta `templates/` de cada skill, p. ej. `skills/ddd-tactical-model-designer/templates/ctlg-agg-okf.md`. Los `SKILL.md` las citan como `templates/...`, ruta que se resuelve contra la carpeta del skill y hasta ahora no las encontraba (estaban solo en `templates/` de la raíz del plugin). Se conservan las copias de la raíz; una prueba verifica que ambas sean idénticas. Eliminar las copias de la raíz queda como decisión posterior.
- Pruebas: `test_ddd_templates_have_expected_types` y `test_all_skills_reference_their_templates` cubren las plantillas de T04 a T06; `test_skill_templates_exist_in_skill_folder` y `test_skill_templates_match_plugin_templates` comprueban la carpeta de cada skill.

## [2.1.1] - 2026-11-21

### Cambiado

- `ddd-domain-discovery`: la salida `domain-discovery.md` se genera con la plantilla tipada `templates/domain-discovery-acp.md` (`type: ACP`, perfil corporativo), alineada con `typed_outputs` del pathmap. Sustituye a la plantilla auxiliar sin frontmatter.
- `ddd-bounded-context-designer`: el catálogo `bounded-contexts.md` se genera con `templates/ctlg-bc-okf.md` (`type: CTLG`, `indexes: BC`), alineado con `typed_outputs` del pathmap. Se elimina la indicación «auxiliar sin tipo OKF».
- Pruebas de plantillas: `test_domain_discovery_template_is_acp_type`, `test_bounded_context_catalog_template_is_ctlg_indexing_bc` y `test_skills_reference_their_typed_templates` sustituyen a la prueba de la plantilla auxiliar.

### Obsoleto

- `templates/domain-discovery-aux.md` queda como marcador de obsolescencia; eliminar el archivo.
- `docs/solicitud-tipo-informe-generico.md` queda sin efecto para `domain-discovery.md`, que usa el tipo `ACP`; cerrar según la gobernanza del estándar.

## [2.1.0] - 2026-11-18

### Añadido

- Plantillas OKF alineadas con STD-OKF-001 v1.9.0-stable para `BC` (`templates/bounded-context-okf.md`) y `CTX` (`templates/context-map-okf.md`), con secciones de responsabilidades, lenguaje, reglas, relaciones y trazabilidad.
- Plantilla auxiliar sin frontmatter OKF para el descubrimiento de dominios (`templates/domain-discovery-aux.md`).
- Solicitud de control de cambios para un tipo documental genérico de informe (`docs/solicitud-tipo-informe-generico.md`). No aprobada.
- Pruebas de plantillas (`tests/test_templates.py`).

### Cambiado

- Las skills `ddd-bounded-context-designer`, `ddd-context-map-designer` y `ddd-domain-discovery` referencian su plantilla de salida.

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

- `scripts/okf_validate.py`: la comprobación de tipos usaba `TYPES`, no definida, y provocaba `NameError` en cualquier documento real; ahora usa la lista `APPROVED`.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


### Corregido

- Documentado en README, DOCUMENTACION y SKILL del orquestador que el plugin se usa igual en Greenfield, Brownfield y Evolution (sin `--scenario` ni reconstrucción del dominio) y que la reconstrucción As-Is la aporta `microservice-api-design` (tipo `ASIS`); prueba en `tests/test_documented_commands.py` (D-22).







## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [0.12.0] - 2026-10-29 (pre-línea base)

### Cambiado

- **Incompatible:** `approve-gate` exige `--actor human:<nombre>`; antes aceptaba cualquier texto (D-07). Ejemplos actualizados.

### Corregido

- Ejemplos de `init` en README, DOCUMENTACION y SKILL del orquestador usan `.comsatel/ddd-domain-design/runs/RUN-001` y `--workspace .`; antes fallaban con `run must be inside` (D-01).
- Documentación y skills: el prefijo de la raíz de runs pasa de `comsatel/<plugin>/runs/` a `.comsatel/<plugin>/runs/`, como define `orchestrator_root` del pathmap (D-04).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [0.11.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/ddd-domain-design/runs/<run-id>/` (campo `orchestrator_root` de `pathmap.json`, que los scripts leen en lugar de la ruta fija `comsatel/`). Las corridas existentes en `comsatel/` hay que migrarlas.

## [0.10.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [0.10.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador acepta los tipos aprobados.

## [0.9.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa. Se amplía el catálogo `PROPOSED` del validador con los 24 tipos nuevos.

## [0.8.1] - 2026-10-25 (pre-línea base)

### Cambiado
- `validate-contract` ahora valida el patrón de relación contra el catálogo de Context Mapping, el contexto propietario de entidades, VO y eventos, y exige actor, evidencia y gate G3 aprobado (`--run`) cuando `approval` es `APPROVED`.
- El validador OKF registra `FDT` (alineado con STD-OKF-001).
- `domain-validation.md` y `domain-design-pack.md` se documentan como salidas auxiliares sin tipo OKF.

### Corregido
- `workflow.py` funciona con `python -I` (ajusta `sys.path`).
- `templates/execution-plan.yaml` usa `design_root: architecture`; README y DOCUMENTACION sincronizados con 0.8.1 y sin instrucciones obsoletas de `design/ddd`.
- Plantillas con `generated.by` en la versión vigente.

## [0.8.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- El validador OKF reconoce `SOL` y `QAR` como tipos propuestos.

## [0.7.1] - 2026-10-24 (pre-línea base)

### Corregido
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: el productor del tipo `IMD` es `biz-information-model-designer` (antes `af-conceptual-model-designer`). Sin cambio de contrato.

## [0.7.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: tipos propuestos de Gestión (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`) y `IMD`/`TRM`; 36 tipos propuestos en total. Cambio aditivo y compatible.
- El validador OKF reconoce los tipos propuestos de Gestión; los acepta hasta el nivel de perfil y los rechaza en publicación, como el resto de tipos propuestos.

## [0.6.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/ddd-domain-design`.
