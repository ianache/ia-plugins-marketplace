# Changelog — kb-quality-consistency-assurance

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


### Cambiado

- Rutas de salida unificadas: los 7 SKILL escriben en `.comsatel/kb-quality-consistency-assurance/runs/<run_id>/` (antes `./comsatel/kb-qca/<run_id>/`, sin punto y con otro nombre). Nuevo `assets/pathmap.json` con `orchestrator_root` y prueba en `tests/test_mod_patterns.py` (D-20). Los runs ya escritos en la ruta anterior deben moverse.

### Corregido

- Mod `hooks/register.js`: el detector de `rm` ahora cubre `-rf`, `-fr`, `-r -f`, `-f -r`, `-Rf` y `--recursive --force`, y el de ramas protegidas cubre `HEAD:main`, `+main`, `refs/heads/main`, `:main` y `--delete main` (antes solo `-rf` y `git push origin main`). Nueva exportación `classify()` y pruebas `tests/mod-risk-patterns.test.mjs` / `tests/test_mod_patterns.py` (D-19).
- README: encabezado con la versión del plugin, aclara que la versión 1.1.0 es la del Mod, documenta las señales detectadas y cómo ejecutar las pruebas. Se verificó que `tests/`, `hooks/hooks.json` y `standards/` existen en el plugin (D-19).


## [1.0.0] - 2026-10-29

### Cambiado

- Línea base absoluta del catálogo: la versión del plugin se reinicia a 1.0.0 por decisión del responsable (todos los plugins parten de 1.0.0). Las versiones anteriores de esta lista son históricas y ya no corresponden a `plugin.json`. Se alinearon README, DOCUMENTACION, VALIDATION, `metadata.version` y `VERSION` de los skills, plantillas y pruebas.

## [1.4.0] - 2026-10-27 (pre-línea base)

### Cambiado
- Sincronización con STD-OKF-001 v1.3.0-stable (94 tipos aprobados, incluidos los de Unidades de Trabajo): copia del estándar reemplaza a v1.3.0-draft; los contratos citan v1.3.0-stable.

## [1.3.0] - 2026-10-26 (pre-línea base)

### Cambiado
- Copia del estándar `STD-OKF-001-v1.3.0-draft.md` sincronizada con el maestro (62 tipos propuestos): se añaden 20 tipos de Infraestructura (`IDS`… `IGR`) y 4 de QA (`TDR`, `TDA`, `EXEC`, `EVD`). Cambio aditivo y compatible; los tipos siguen pendientes de aprobación corporativa.

## [1.2.1] - 2026-10-26 (pre-línea base)

### Corregido
- `kb-quality-orchestrator/SKILL.md`: la ruta de `validate_workflow.py` apuntaba a `scripts/` dentro de la carpeta del skill, donde no existe; ahora es `../../scripts/validate_workflow.py` y se aclara que recibe el plan en JSON.

## [1.2.0] - 2026-10-24 (pre-línea base)

### Cambiado
- Estándar `STD-OKF-001-v1.3.0-draft.md` sincronizado con el maestro (38 tipos propuestos): se añaden `SOL` (Solution Proposal) y `QAR` (KB Quality Report), y `DSP` pasa a llamarse *Development Scope Pack* (la sigla no cambia). Cambio aditivo y compatible.
- Se incorpora la copia del estándar en `standards/`; el informe `QAR` queda registrado.

## [1.1.0] - 2026-10-24 (pre-línea base)

### Añadido
- Línea base del registro de cambios; los anteriores están en `git log`.
