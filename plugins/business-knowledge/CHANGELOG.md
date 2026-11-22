# Changelog — business-knowledge

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/); versionado según [SemVer 2.0.0](https://semver.org/lang/es/). La versión vigente está en `.claude-plugin/plugin.json`.

## [Sin publicar]

### Cambiado

- Adopción de STD-OKF-001 v1.9.0-stable; las salidas documentales de skills especialistas llevan tipo y metadatos OKF.


## [2.3.0] - 2026-11-08

### Corregido

- `biz-glossary-curator`: `glossary.py check` rechaza documentos que no sean `TRM-*.md` o `CTLG-TRM.md` en `business/terms/`; el skill documenta que no se crea un glosario con otro `type`.

### Añadido

- `validate_pathmap.py`: catálogo de área `indexes: AREA`, ubicado en la raíz de `business/` (índice general de la carpeta de negocio, sin tipo de documento propio).


## [2.2.0] - 2026-11-07

### Añadido

- `biz-rules-modeler`: procedimiento de reutilización de reglas existentes antes de numerar, y sección de catálogos narrativos (`CTLG` con `indexes: BR`).
- `biz-rules-modeler`: lista de comprobación para migrar documentos de reglas heredados (`references/migracion-documentos-heredados.md`).
- `validate_pathmap.py`: un `CTLG` sin entrada en `pathmap.json` se valida si declara `indexes` con un tipo mapeado; se ubica en el directorio de ese tipo.

### Corregido

- `validate_okf.py`: el error de fuente sin `resource` indica cómo citar una fuente eliminada (referencia de git).

## [2.1.0] - 2026-11-07

### Añadido

- Tipo `BSN` (Business Scenario) en STD-OKF-001 v1.8.0-stable, aprobado por el responsable y con revisión de semántica aprobada el 2026-11-07. Aditivo: ningún tipo existente cambia.
- Skill `biz-scenario-modeler` (VERSION 1.0.0): modela escenarios de negocio como secuencias de reglas `BR` con precondiciones, pasos, excepciones y resultado, trazados a `BR`, `TRM`, `BCAP` y `BO`.
- `templates/scenario.md`: contrato de contenido del `BSN`, con frontmatter y las once secciones obligatorias.
- `scripts/check_scenario.py`: verifica las secciones, que cada paso cite una `BR` existente, que los `TRM` citados existan (con `--workspace`), readiness válido y ausencia de marcadores de plantilla.
- Ruta `business/scenarios/` y prefijo `BSN-NNN` en `assets/pathmap.json`.
- Pruebas `ScenarioTests` y `BSN` en las pruebas de pathmap y de estructura.
- Tarea `T07` (`biz-scenario-modeler`, entregable `BSN`) en el orquestador: cierra en G5 y depende de T04 (G4), no de T05 (IMD). T06 (G6) depende de T05 y T07.
- `check_pack.py`: un `BSN` que cite una `BR` inexistente en el pack es un error; un `BSN` sin ninguna `BR` es un aviso de trazabilidad.
- `biz-scenario-modeler`: `references/` completas (contrato, política de rutas, perfil OKF, guía técnica), sección de mapeo de rutas en `SKILL.md` y un ejemplo `BSN-001` que pasa `validate.py` y `check_scenario.py`.
- Documentación del orquestador, `COVERAGE-MATRIX.md` y `VALIDATION.md` con `T07` y `BSN`.

### Cambiado

- `validate_okf.py` y `check_pack.py` reconocen `BSN`; `BSN` exige `product`, `pack` y `skill`.
- Referencias a STD-OKF-001 pasan de v1.7.0-stable a v1.8.0-stable en documentación, validadores y pathmap.
- `assets/pathmap.md` cuenta siete skills especializados.
- Omitir G5 con `--omit G5` omite T05 (IMD) y T07 (BSN): ambos cierran en G5. Requiere justificación; la justificación debe indicar que no se necesitan escenarios de negocio.

## [2.0.0] - 2026-11-07

### Añadido

- `rules.py` en `biz-rules-modeler`: `from-json` genera un `BR-NNN.md` por regla de un lote (todo o nada), `new`, `build` (regenera el catálogo) y `check` (validación de cada regla y correspondencia 1:1 con el catálogo).
- `validate_pathmap.py --check-catalog BR|TRM`: correspondencia 1:1 entre cada documento y su catálogo; `CTLG` se valida por ID hacia su directorio (`catalogs` de `pathmap.json`).

### Cambiado

- **Incompatible:** el índice de términos y de reglas pasa a ser un catálogo `type: CTLG` con frontmatter OKF completo: `business/terms/CTLG-TRM.md` y `business/rules/CTLG-BR.md`. El catálogo lista ID, título, estado y versión con enlace; ya no repite definiciones ni enunciados.
- **Incompatible:** `pathmap_version` pasa a `2.0.0`; el orchestrator rechaza planes con la versión anterior.
- `glossary.py build` y `check` operan sobre `CTLG-TRM.md`; `check_pack.py` valida los catálogos 1:1 con sus documentos.
- Nombres de archivo corregidos en `assets/pathmap.json` (`TRM-NNN-<slug>.md` y `BR-NNN.md`, sin el texto `+ index.md` que los acompañaba).

### Eliminado

- **Incompatible:** `index.md` en `business/terms/` y `business/rules/`, y la plantilla `templates/business-rules-index.md`. `build` elimina un `index.md` obsoleto y `check` lo reporta como error.

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM` (el catálogo es `CTLG-TRM.md`, no `terms/index.md`).
- Las reglas de negocio no tenían un archivo por regla ni validación que lo exigiera; ahora el generador escribe uno por regla y el check comprueba la correspondencia 1:1.
- El catálogo de términos y reglas no declaraba un tipo OKF ni pasaba por el validador (los `index.md` se omitían); ahora es `type: CTLG` y se valida.

## [1.2.0] - 2026-11-07

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md` (ampliación v1.7.0: tipo `EPC`, aprobado el 2026-11-07). Lista de tipos aprobados del validador regenerada desde la maestra. Sin cambios de contrato en los skills.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


### Añadido

- `init --omit G5 --justification`: permite omitir T05/G5 (IMD) en cualquier escenario cuando el cambio no toca el modelo de información; requiere justificación y T06 pasa a depender de G4. README, SKILL y pruebas actualizados (D-24a).

### Cambiado

- **Endurecimiento (incompatible, D-21a):** `transition` (a `NEEDS_REVIEW`/`DONE`) y `approve-gate` exigen `--evidence` con un archivo existente dentro del workspace y guardan su ruta relativa; el texto libre se rechaza. Copias actualizadas en el SKILL del orquestador.
- README y SKILL del orquestador documentan que `brownfield` y `evolution` generan el mismo plan que `greenfield` y que partir de la línea base depende de la revisión humana (D-21c).







## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [2.0.1] - 2026-10-29 (pre-línea base)

### Corregido

- Documentación y skills: el prefijo de la raíz de runs pasa de `comsatel/<plugin>/runs/` a `.comsatel/<plugin>/runs/`, como define `orchestrator_root` del pathmap (D-04).
- Encabezados de versión de README/DOCUMENTACION/VALIDATION alineados con `plugin.json` (D-08).

## [2.0.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/business-knowledge/runs/<run-id>/` (campo `orchestrator_root` de `pathmap.json`, que los scripts leen en lugar de la ruta fija `comsatel/`). Las corridas existentes en `comsatel/` hay que migrarlas.

## [1.4.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [1.4.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; el validador y los textos tratan `TRM`, `BCP`, `BO`, `STK`, `BCAP` e `IMD` como aprobados.

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

### Cambiado
- Copia de `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro: tipos propuestos de Gestión (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`) y `IMD`/`TRM`; 36 tipos propuestos en total. Cambio aditivo y compatible.
- El validador OKF reconoce los tipos propuestos de Gestión; los acepta hasta el nivel de perfil y los rechaza en publicación, como el resto de tipos propuestos.

## [1.0.0] - 2026-10-24

### Añadido
- Línea base del registro de cambios. Los cambios anteriores a esta versión no están documentados aquí; consultar `git log -- plugins/business-knowledge`.
