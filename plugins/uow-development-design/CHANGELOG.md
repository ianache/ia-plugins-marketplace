# Changelog — uow-development-design

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

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.


### Añadido

- `init --baseline-repo <repo>`: G0 verifica con `git cat-file -e` que `--baseline-commit` existe (check `baseline-commit-exists`); un hash inventado bloquea G0 (D-23a).
- UCM: campos `backward_compatibility` y `rollback` con secciones `## Compatibilidad hacia atrás` y `## Rollback`, obligatorios en EVOLUTION, y check `compat-and-rollback-present` (tipo `script`) en `CODEBASE_GATE`; actualizados `check_uow_package.py` (7 copias), plantilla, política y pruebas (D-25). **Endurece el gate en EVOLUTION (incompatible).**

### Cambiado

- **Endurecimiento de gate (incompatible, D-18):** `uow_orchestrator.py gate` ya no acepta PASS declarados. Con `--pack` ejecuta `check_uow_package.py` (perfil del gate, `runners` de `gate-policies.yaml`) y su resultado manda; los checks `script` sin verificador exigen `attested_by: human:<id>` y los `independent-review` un `reviewer` (`human:<id>` o `agent:<skill>`) distinto del autor y del orquestador. `--checks` acepta la lista o `{"checks": [...]}` y rechaza con mensaje claro las entradas inválidas. La evidencia registra `source` y `declared_result_ignored`. Los flujos que pasaban un JSON a mano con todo PASS deben usar `--pack`, atestación o revisor.

### Corregido

- `uow_orchestrator.py`: `--human-approval`, `--checks`, `--waiver` y `--scope-json` documentan en `--help` que reciben la ruta de un archivo JSON; un valor inválido se rechaza con un mensaje claro en lugar de una traza (D-18).
- README: sección sobre la aprobación humana y el flujo `BLOCKED` → `human --decision REVALIDATE` → `gate` (D-18). Prueba `tests/test_rutas_docs.py` para la ruta `.comsatel/uow-development-design/runs/`.



## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [0.4.0] - 2026-10-29 (pre-línea base)

### Cambiado

- **Incompatible:** la raíz de estado operativo pasa a `.comsatel/uow-development-design/runs/` (`orchestrator_root` del pathmap; D-05). Los runs existentes en la ruta anterior (`.comsatel/uow-development-design/`) deben moverse o reiniciarse. Textos, contratos, gates y pruebas actualizados.

## [0.3.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente y `assets/pathmap.md` solo conserva las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace. Incompatible: el estado operativo del orchestrator pasa a `.comsatel/uow-development-design/` (campo `orchestrator_root` de `pathmap.json`; el valor por defecto de `--root` lo lee de ahí). Las corridas existentes en `comsatel/` hay que migrarlas.

## [0.2.1] - 2026-10-27 (pre-línea base)

### Cambiado
- Mapeo de rutas unificado: `assets/pathmap.json` es la única fuente (`document_types`, `artifacts`, `pathmap_version`); `assets/pathmap.md` conserva solo las reglas de ejecución; `OUTPUT-PATH-POLICY.md` pasa a ser un enlace; los scripts (`validate_pathmap.py`, `workflow.py`) leen el JSON en lugar de duplicar el mapa. Sin cambio de rutas.

## [0.2.0] - 2026-10-27 (pre-línea base)

### Añadido
- Caso sintético `examples/geocercas-alta/` (US-101, modo BROWNFIELD): insumos, paquete UOW esperado con digest, `verify_example.py` con controles negativos y prueba en `tests/test_uow_plugin.py`.

### Cambiado
- Los tipos `UOW`, `UCX`, `UCB`, `UCM`, `UAP` y `UWR` pasan de propuestos a aprobados: STD-OKF-001 v1.3.0-stable los incorpora (94 tipos) y reemplaza a v1.3.0-draft en el estándar y en las copias de cada skill.

## [0.1.0] - 2026-10-27 (pre-línea base)

### Añadido
- Plugin nuevo con 1 orquestador y 6 especialistas para convertir una User Story, el diseño de API y el diseño de BD en Unidades de Trabajo (UOW) asignables a un developer con agente IA.
- Tipos documentales `UOW`, `UCX`, `UCB`, `UCM`, `UAP` y `UWR` (propuestos en STD-OKF-001 v1.3.0-draft, 68 tipos propuestos; pendientes de aprobación).
- Orquestador fail-closed (`uow_orchestrator.py`) con `expand` por UOW, G0 con modo y línea base, y `UOW_READY_GATE` de aprobación humana ligada al digest del paquete (`uow_package.py`).
- Siete gates con checks deterministas (`check_uow_package.py`) y checks de revisión independiente.
- Perfil de ejecución Claude Code con Superpowers (plan en formato `writing-plans` y brief para `CLAUDE.md`).
- Pruebas por skill y del plugin.
- Registro en `.claude-plugin/marketplace.json`.
