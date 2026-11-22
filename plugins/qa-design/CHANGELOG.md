# Changelog — qa-design

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

## [3.0.0] - 2026-11-21

### Cambiado (incompatible)

- El TC declara sus historias en `user_stories: [US-NNN, ...]` (una o más) en lugar de `user_story: US-NNN`. Los TC ya emitidos con `user_story` dejan de cumplir `check_tc_detail.py` y deben migrarse.
- SSP: `user_stories: [US-n, ...]` obligatorio en su frontmatter. Un SSP sin historias bloquea `init`. El check `ssp-tc-selection` de T03 selecciona los TC que comparten historia con el SSP (`plan.ssp_tc_ids`); una historia del SSP sin TC bloquea el gate. El TC no se duplica por SSP.
- `qa-agentic-test-engineer` 1.7.0 → 1.8.0: check `ssp-scope-respected` en `TEST_ENGINEERING_GATE` (AT y EXEC dentro de la selección del SSP) y sección «Alcance SSP».
- `qa-sdlc-orchestrator` 1.7.0 → 2.0.0 (entrada SSP sin DSP y `ssp-tc-selection`).
- `qa-test-design` 1.6.0 → 2.0.0: plantilla `TestCase-OKF.md`, ejemplo `TC-API-017.md`, validador `check_tc_detail.py` (obligatorio, formato `US-n` y cruce con la trazabilidad) y esquema `test-case.schema.yaml`.

## [2.4.0] - 2026-11-21

### Añadido

- `qa_orchestrator.py init` acepta un SSP como entrada sin DSP: `--ssp-id` y `--ssp-path` bastan. El DSP se toma del `dsp_id` del SSP y se localiza en la KB (`--kb-root`), por `sources` del SSP o por búsqueda única. Si no se localiza, no es único o no declara versión, el init se bloquea. Pruebas en `skills/qa-sdlc-orchestrator/tests/test_ssp_input.py`.

### Cambiado

- `qa-sdlc-orchestrator` 1.6.0 → 1.7.0. El SSP solo selecciona alcance: el TC lo define el DSP y no se duplica por SSP.

## [2.3.0] - 2026-11-21

### Añadido

- Skill `web-automation` (subordinado de `T05-WEB`, 1.0.0): implementa los TC web aprobados con Playwright o Selenium en `test/functional/<framework>/` del AUT, con reporte por AUT `automated-tests/web/<aut>/web-automation-report.yaml` y validador `scripts/validar_reporte_web.py`.
- Check `web-automation-subordinate-traceable` en `TEST_ENGINEERING_GATE` (plantilla del engineer y `gate-policies.yaml` del orquestador), con pruebas en `tests/test_web_subordinate.py`.

### Cambiado

- `qa-agentic-test-engineer` 1.6.0 → 1.7.0: describe el subordinado web en su `SKILL.md` y aplica el nuevo check en el perfil engineering.

## [2.2.0] - 2026-11-21

### Cambiado

- `gate-report.yaml` (registro operativo que escriben seis skills especialistas como gate_proposal, con la misma estructura) se mueve a `skills/qa-sdlc-orchestrator/templates/`: los registros de control del flujo los mantiene el orquestador. Se eliminan las seis copias de `skills/*/templates/` y la carpeta `templates/` de la raíz. Los checks de cada gate siguen en `resources/gates/<GATE>.yaml` del skill productor. Plantilla con marcadores `<GATE>`, `<TASK_ID>`, `<skill>/<version>` y `<check-id>`.
- Pruebas: `test_templates_do_not_declare_gate_decision` de los seis `test_skill_contract.py` lee la plantilla del orquestador; `tests/test_qa_plugin.py` añade la clase `Plantillas`, que comprueba que no existe `templates/` en la raíz, que `gate-report.yaml` está en la carpeta del orquestador y que no se duplica en los skills.
- Versión de los seis skills especialistas afectados: `1.5.0` → `1.6.0`. `qa-sdlc-orchestrator`: `1.5.0` → `1.6.0` (recibe la plantilla de `gate-report`).

## [2.1.0] - 2026-11-20

### Cambiado

- **Asignación de microservicios por `api_id` después de T03.** `init` declara solo los microservicios involucrados (`scope.microservices` con `id` = `api_id`); ya no admite listas `tc_funcional` / `tc_carga`. G0 exige al menos un microservicio cuando hay superficie `API`.
- **Frontmatter de TC (`tc_contract` 1.4):** `api_id` obligatorio cuando `surface: API`, igual al `api_id` de la tabla Surface Target. Los TC `tc_contract` 1.3 siguen validándose, pero también deben declarar `api_id`.
- **T03:** nuevo check `tc-api-assigned` (calculado por el orquestador): cada TC API debe declarar un `api_id` declarado en G0.
- **Subordinados:** se crean tras T03 a partir de los TC `READY` agrupados por `api_id` y tipo (`rendimiento` → `SUB-<api_id>-CARGA`, resto → `SUB-<api_id>-FUN`).

### Pruebas

- `test_ssp_scope.py`: pruebas de subordinados reescritas para la asignación por `api_id`.
- `test_testcase_contract.py`: pruebas de `api_id` (obligatorio, coherente con la tabla, no exigido en superficies no API).

## [2.0.0] - 2026-11-20

### Cambiado

- **Cambio incompatible: reintentos desactivados en todos los gates** (`max_retries: 0`): el primer `FAIL` de un gate `CONDITIONAL_HIL` bloquea y abre intervención humana, sin `AUTO_RETRY`. Afecta a `FEATURE_ANALYSIS_GATE`, `TEST_DESIGN_GATE`, `TEST_DESIGN_REVIEW_GATE`, `TEST_ENGINEERING_GATE`, `TEST_ENGINEERING_REVIEW_GATE` y `QUALITY_INTELLIGENCE_GATE`. Un `FAIL` ya no se recupera con un reintento automático; con `halt_scope: all` detiene la ejecución completa hasta la decisión humana. Ver `REGISTRO-DESACTIVACION-REINTENTOS.md`.

### Pruebas

- `test_orchestrator.py`: `test_fail_retries_then_blocks` sustituida por `test_fail_blocks_without_retry`.

## [1.9.0] - 2026-11-16

### Añadido

- **Integración de `loadtest-automation` como subordinado de T05-API.** Los AT de TC `rendimiento` se verifican con el check `load-automation-subordinate-traceable` del gate de ingeniería: reporte en `automated-tests/k6/<microservicio>/loadtest-automation-report.yaml`, criterio declarado (BASELINE o APROBADO con fuente), TC `IMPLEMENTED` y `k6.estado` `EXECUTED`.
- Orquestador: T05-API referencia un subordinado por microservicio API y tipo de prueba (`SUB-<ms>-FUN` con postman-automation, `SUB-<ms>-CARGA` con loadtest-automation), declarados en `scope.microservices` (`tc_funcional`, `tc_carga`). G0 añade `subordinates-declared` y rechaza un TC asignado a dos subordinados.

### Cambiado

- `api-automation-subordinate-traceable` deja de exigir postman-automation para los TC `test_type: rendimiento`.
- `loadtest-automation`: los TC de carga se identifican por `test_type: rendimiento`, valor del enum de TC; antes se mencionaba también "carga", que no existe en el enum.

### Clasificación de skills

- El plan compone seis skills especializados más el orquestador. `postman-automation` y `loadtest-automation` son **subordinados**: no tienen tarea propia en el plan y los invoca `qa-agentic-test-engineer` dentro de T05-API. Por eso no cuentan como especialistas del plan. Se mantienen separados porque tienen contratos y reportes distintos.

### Pruebas

- Engineer: 36 pruebas (10 nuevas en `tests/test_load_subordinate.py`). Orquestador: 84.

## [1.8.0] - 2026-11-16

### Añadido

- Skill `loadtest-automation` (1.0.0): convierte los TC de carga o rendimiento de un microservicio HTTP en una suite Grafana k6 en `test/load/`: `k6.js` principal, un módulo `scenarios/TC-<ID>.js` por caso, `lib/config.js` para variables de entorno y `data/` para datos. Incluye `scripts/validar_k6.py` (checks L1–L7, códigos de salida 0/1/2), pruebas en `tests/` y `references/estructura-k6.md`.
- Criterio de umbrales: la suite declara `BASELINE` (sin umbrales, solo línea base) o `APROBADO <DATA-xx|NFR-xx>` (umbrales con `umbral-fuente`). Sigue `STD-TEST-FLOTAS` §7, que prohíbe declarar aprobado o fallido contra cifras no cerradas.
- Justificación del octavo especialista: sigue el mismo criterio que `postman-automation` (dominio de carga sin cobertura por otro skill). Queda como excepción documentada a la recomendación de seis especialistas.

### Pendiente

- Integración de `loadtest-automation` como subordinado de T05-API y check de carga en el gate de ingeniería: no implementada.

## [1.7.0] - 2026-11-16

### Añadido

- **Alcance SSP en el orquestador:** `init --ssp-id <SSP> --ssp-path <documento>` fija el SSP como fuente del plan (`ssp_source`: documento, digest y DSP declarado). G0 añade `ssp-identified` y `ssp-belongs-to-dsp`; sin SSP registra `ssp-scope`. Cada T05 recibe `scope_ssp`.
- **Automatización API subordinada:** T05-API declara `subordinate_skills: [postman-automation]`. El engineer delega ahí los AT de superficie API.
- **Check `api-automation-subordinate-traceable`** en el gate de ingeniería (script, perfil engineering y `TEST_ENGINEERING_GATE`): exige el reporte de postman-automation, que cada AT API corresponda a un TC `AUTOMATED` o `PARTIAL`, y `newman.estado` `EXECUTED`.

### Cambiado

- `init` sin `--ssp-path` con `--ssp-id` ahora se rechaza. Los planes sin SSP no cambian.
- `ssp_ref` sigue siendo el ID del SSP (compatibilidad); la identidad completa va en `ssp_source`.

### Pruebas

- Orquestador: 78 pruebas (8 nuevas en `tests/test_ssp_scope.py`).
- Engineer: 26 pruebas (7 nuevas en `tests/test_api_subordinate.py`).

## [1.6.0] - 2026-11-16

### Añadido

- Skill `postman-automation` (1.0.0): consolida los TC `READY` de un microservicio API en una colección Postman con estructura `RF##-<funcionalidad>` / `<ID> - <Nombre>` y documentación por request con objetivo y criterios de aceptación extraídos de la historia. Incluye `scripts/validar_coleccion.py` (validador determinista, códigos de salida 0/1/2), pruebas en `tests/` y la referencia `references/estructura-coleccion.md`.
- Justificación del séptimo especialista: el plugin tenía seis especialistas, el máximo recomendado por la guía. `postman-automation` cubre un dominio que ningún skill existente trata (colecciones Postman de API por funcionalidad); `qa-agentic-test-engineer` es genérico y no define esa estructura. Queda como excepción documentada para revisión.

## [1.5.0] - 2026-11-07

### Cambiado

- Propagación de STD-OKF-001 v1.8.0-stable (tipo `BSN`, ampliación aditiva): copia del estándar, referencias a la versión y lista de tipos aprobados de los validadores. Sin cambios de contrato de skills.

## [1.4.1] - 2026-11-07

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM`. El catálogo de términos es `business/terms/CTLG-TRM.md` (tipo `CTLG`), no `business/terms/index.md`. Corrección textual; sin cambios de contrato.

## [1.4.0] - 2026-11-07

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md` (ampliación v1.7.0: tipo `EPC`, aprobado el 2026-11-07). Lista de tipos aprobados del validador regenerada desde la maestra. Sin cambios de contrato en los skills.

## [1.3.0] - 2026-11-04

### Añadido

- **Contrato TestCase 1.3 (opt-in con `tc_contract: "1.3"`):** `TestCase-OKF.md` añade `## Intención`, `Pass when` / `Fail when` en el oracle, `Idempotencia` y `cleanup.required` / `cleanup.strategy_ref`, `## Requisitos de evidencia` por modo, `## Restricciones de ejecución` y `## Trazabilidad` (representación del frontmatter), además de `test_level` y `criticality`. El perfil STD-OKF-001 y las tablas se mantienen.
- `resources/schemas/test-case.schema.yaml`: contrato declarativo cuyas enumeraciones verifica una prueba frente al validador.
- `examples/TC-API-017.md`: TC de referencia que cumple el contrato 1.3.
- Vocabulario `testcase_vocabulary` y reglas de TC (`testcase_execution_neutral`, `execution_mode_owner`, `automated_test_requires_approved_testcase`) en `common-contract.yaml` de los 7 skills; invariantes de TC y AT en `qa-pack-contracts.yaml`.
- Responsabilidades y dimensiones de revisión en los SKILL de `qa-test-design`, `qa-test-design-reviewer` y `qa-agentic-test-engineer` (validación previa a AT con `testcase_ref`).
- Cuerpo del issue de GitLab `TestCase` con `intent_summary`, `test_level`, `test_type`, `priority`, `criticality` y `automation_status` (solo referencias ligeras, sin pasos).

### Cambiado

- `check_tc_detail.py`: un TC con `tc_contract: "1.3"` debe cumplir las reglas nuevas (restricciones, evidencia, cleanup, trazabilidad, enumeraciones, Surface Target por superficie, IDs de paso y TDR referenciados y sin placeholders). Los TC sin `tc_contract` siguen con las reglas previas y se listan como legacy; no se migran masivamente.

### Corregido

- `check_tc_detail.py` ya no confunde la cabecera `TDR-ID` de la tabla de datos con un identificador de TDR.

## [1.2.0] - 2026-11-04


### Añadido

- Regresión: plantilla del `QTS` con `## Estrategia de regresión` (selección por impacto con el `IMP`, caracterización de la línea base, humo y retest) y del `QTP` con `## Selección de regresión`; documentado en el SKILL de `qa-test-design` y verificado por prueba (D-26a).

### Cambiado

- **Entregables por DSP y SSP (incompatible):** los entregables QA pasan de `testing/` a `testing/<DSP-ID>/` y, con `--ssp-id`, a `testing/<DSP-ID>/<SSP-ID>/`. Sin versión: las pruebas pertenecen a un DSP y SSP concretos. `init` valida los identificadores y guarda `deliverable_root` y `ssp_ref` en el plan. `pathmap.json` (tipos relativos a la raíz), `pathmap.md`, `DOCUMENTACION.md` y los SKILL de los cinco especialistas actualizados; pruebas `DeliverableFolders` añadidas.
- **Estado por run (incompatible; versión MINOR por decisión del responsable; `pathmap_version` 1.1.0):** el estado operativo pasa de `.comsatel/qa-design/runs/` a `.comsatel/qa-design/runs/<run-id>/`, igual que requirements-engineering. `qa_orchestrator.py` exige `--run-id` (validado: sin separadores ni `..`) y el plan de un run no se sobrescribe. Ejecuciones distintas ya no comparten `plan.yaml`, estado, `events.jsonl` ni evidencia. Contratos, gates, plantillas, SKILLs y pruebas actualizados; pruebas `RunIsolation` añadidas. Los runs creados con la ruta anterior deben moverse a `runs/<run-id>/`. Plugin y los 7 skills pasan a 1.2.0 (MINOR sobre 1.1.0 de main), por decisión del responsable; la prueba de metadatos exige versiones homogéneas entre plugin y skills.
- **Endurecimiento de gate (incompatible, D-14):** `qa_orchestrator.py gate` ya no acepta PASS declarados. Ejecuta por su cuenta los verificadores `runners` de `gate-policies.yaml` (diseño, revisión de diseño, ingeniería y revisión de ingeniería; nuevas opciones `--pack`, `--design-pack`, `--critical-risks`) y su resultado manda sobre el JSON. Un check `script` sin verificador solo pasa con `attested_by: human:<id>`; un `independent-review` exige `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor y del orquestador. La evidencia registra el origen (`script`, `human-attested`, `independent-review`) y `declared_result_ignored`. Los flujos que pasaban un JSON a mano con todo en PASS deben añadir atestación o revisor.

### Corregido

- `qa_orchestrator.py gate --checks` acepta la lista de checks o la salida de los `check_*.py` (`{"checks": [...]}`), valida tipos y rechaza con mensaje claro (sin traza) las entradas inválidas y las salidas con `error`; pruebas con la salida real del script (D-16).
- Docstrings de los `check_test_design.py` y `check_test_engineering.py`: el orquestador no añade los checks `independent-review`; los aporta quien revisa (D-14, evidencia 2).
- `DOCUMENTACION.md`: la tabla de gates lista los checks de `gate-policies.yaml` (11 en `TEST_DESIGN_GATE` y 11 en `TEST_DESIGN_REVIEW_GATE`; también se corrigieron `TEST_ENGINEERING_GATE`, `TEST_ENGINEERING_REVIEW_GATE` y `QUALITY_INTELLIGENCE_GATE`); prueba que compara ambos (D-14, evidencia 3).



## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.

## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [6.0.0] - 2026-10-29 (pre-línea base)

### Cambiado

- **Incompatible:** la raíz de estado operativo pasa a `.comsatel/qa-design/runs/` (`orchestrator_root` del pathmap; D-05). Los runs existentes en la ruta anterior (`.comsatel/qa-sdlc-pack/`) deben moverse o reiniciarse. Textos, contratos, gates y pruebas actualizados. Los textos que escribían `./comsatel/qa-sdlc-pack/` (sin punto) también se corrigen. Versión de plugin y de los 7 skills alineadas a 6.0.0.

## [5.5.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Se introduce `assets/pathmap.json` (`orchestrator_root`, `orchestrator_files`) y `assets/pathmap.md` con las reglas de ejecución; `qa_orchestrator.py` lee `orchestrator_root` para el valor por defecto de `--root`. `pathmap.json` incluye el mapeo de los 16 tipos documentales QA (`document_types`, `artifacts`) bajo `deliverable_root` (`testing/`). Sin cambio de rutas.

## [5.5.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Las copias del estándar de los 7 skills se sincronizan con el maestro STD-OKF-001 v1.3.0-stable (94 tipos): los tipos QA (`QFA`, `QTD`, `QTP`, `QTR`, `TSN`, `QTE`, `AT`, `QER`, `QQI`, `QDC`, `TDR`, `TDA`, `EXEC`, `EVD`) pasan de propuestos a aprobados.


## [5.4.0] - 2026-10-26 (pre-línea base)

Implementa las instrucciones de ajuste del 2026-10-26 sobre los 7 skills existentes (no se crean skills nuevos; el plugin y los 7 skills pasan a 5.4.0). Contiene cambios incompatibles en el contrato de TC.

### Añadido
- **Test Data (TDR / TDA):** `qa-test-design` produce `test-data-plan.md` y un `TDR-*` por requisito de datos (QUÉ datos); `qa-agentic-test-engineer` los materializa como `TDA-*` con `test-data-generation-plan.md`, `test-data-manifest.yaml` y `test-data/{datasets,fixtures,scripts}` (CÓMO). Trazabilidad `TC → TDR → TDA → EXEC → EVD`.
- **Tres modos de ejecución** en cada `EXEC` (`MANUAL`, `AUTOMATED_STANDALONE`, `AUTOMATED_CICD`) y `automation_status` en el TC. GitLab CI/CD como execution engine: `cicd/ci-test-execution.yaml`, fragmento `.gitlab-ci` y procedencia de pipeline/job en la EXEC.
- Plantillas: `TDR-OKF`, `test-data-plan` (qa-test-design); `Execution-OKF`, `Evidence-OKF`, `TDA-OKF`, `test-data-generation-plan`, `test-data-manifest.yaml`, `ci-test-execution.yaml`, `gitlab-ci-test.yml` y plantillas de dataset, fixture y script (qa-agentic-test-engineer).
- Scripts: `check_test_engineering.py` (engineer y revisor), `quality_metrics.py` (qa-quality-intelligence, métricas segmentadas) y `exec_readiness.py` (orquestador).
- Gates: nuevos checks de datos (`test-data-requirements-defined`, `test-data-safe`, `test-data-plan-reviewed`), de ingeniería (`tda-traces-to-tdr-and-tc`, `test-data-ready`, `execution-mode-requirements`, `cicd-provenance-complete`, `no-unauthorized-pii`), de revisión por modo y de Quality Intelligence (`results-segmented-by-mode`, `failures-classified-by-cause`).
- Pruebas del plugin (`tests/test_qa_plugin.py`) y pruebas nuevas por skill.
- Estándar: `TDR`, `TDA`, `EXEC` y `EVD` se proponen en STD-OKF-001 v1.3.0-draft (62 tipos propuestos); copias de los 7 skills sincronizadas.

### Cambiado (incompatible)
- El campo `execution` del frontmatter del TC se reemplaza por `automation_status`; el modo de ejecución pertenece a la EXEC.
- El orquestador renombra `execution_modes` del plan a `workflow_modes` y `execution_mode` de las tareas a `scheduling_mode`, para que `execution_mode` signifique solo el modo de ejecución de una EXEC.
- Los gates `TEST_DESIGN_GATE`, `TEST_DESIGN_REVIEW_GATE`, `TEST_ENGINEERING_GATE`, `TEST_ENGINEERING_REVIEW_GATE` y `QUALITY_INTELLIGENCE_GATE` añaden checks; las plantillas de estrategia y plan incluyen las secciones de datos, actividades y prioridades.
- En el frontmatter de EXEC y TDA el resultado y la preparación usan `result` y `readiness` (`status` queda reservado al estado documental).

### Corregido
- `qa-pack-contracts.yaml` (7 copias) no parseaba: un `
` literal dentro de un comentario dejaba `packs:` comentado.
- `TEST_DESIGN_REVIEW_GATE.yaml` tenía un check mal indentado y la política del orquestador no incluía `tc-detail-complete` ni `surface-target-complete`; los dos tests asociados estaban en rojo.

## [5.3.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- Las 7 copias del estándar dentro de los skills, que estaban en una versión anterior (1.0.0), se reemplazan por la vigente. Los skills no cambian.

## [5.2.1] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/qa-design`.
