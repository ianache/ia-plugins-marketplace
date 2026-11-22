# Changelog

Formato: Keep a Changelog. Versionado: SemVer.

## [Sin publicar]

## [1.1.0] - 2026-11-21

### Cambiado

- Copia del estándar STD-OKF-001 propagada desde el maestro `v1.11.0-stable`: añade el tipo `IRP` (Informe o Reporte genérico) a la lista de tipos del validador; `QTD` pasa a cobertura, trazabilidad, TSN y TC, con estrategia y plan en `QTP`; incorpora la aclaración v1.9.0 sobre salidas de especialistas.


### Cambiado
- Preparada la siguiente versión mayor (plugin.json 1.0.0) por cambios incompatibles de tipos, rutas y contratos, en alineación con `plugin-skills-guideline.md` y STD-OKF-001 v1.9.0-stable.
- Se conserva la estructura de un orchestrator y cinco skills especializados (dentro del máximo recomendado de seis).
- Solo `STR` y `CLS`, tipos aprobados, se publican como documentos OKF. `RVA`, `RTA`, `RTX` y `RRD` se retiraron como tipos: agendas, payloads de experimento y readiness son operativos.
- El orchestrator mantiene manifiesto, plan, registro de gates, payloads y evidencia en `.comsatel/ssp-closure/runs/<run-id>/`; entregables conceptuales permanecen en `management/`.
- `workflow.py` crea la estructura del run, rechaza IDs inseguros y no sobrescribe runs. Para aprobar, exige propuesta `READY`, evidencia y gates dependientes aprobados. `validate_pathmap.py` valida el mapeo aprobado.
- Se agregaron pathmap, contratos completos, `VALIDATION.md` y perfil local STD-OKF-001 v1.9.0. Greenfield/Brownfield/Evolution se declaran fuera del alcance de este workflow de cierre.

### Migración
- Migrar manualmente los runs de `comsatel/ssp-closure/runs/<run-id>/` a `.comsatel/ssp-closure/runs/<run-id>/`; el script no mueve datos anteriores.
- Migrar agendas/issues sin tipo a payloads operativos e integrar el contenido semántico en `STR` o `CLS`. No reetiquetar `RVA`, `RTA`, `RTX` o `RRD` con otro tipo.

## [0.3.0] - 2026-11-12

### Cambiado
- Las plantillas se movieron a `skills/<skill>/templates/deliverable.md`, una por skill, con frontmatter OKF (`type`, `id`, `title`, `description`, `version`, `status`, `owner`, `classification`, `tags`, `pack`, `skill`, `generated`, `sources`).
- Cada plantilla tiene su tipo documental:
  - `review-status-report` â†’ `STR` (aprobado en STD-OKF-001 v1.8.0-stable).
  - `review-agenda` â†’ `RVA`, `retro-agenda` â†’ `RTA`, `retro-experiment-tracker` â†’ `RTX`, `release-readiness` â†’ `RRD`: **propuestos, sin aprobar**. Requieren control de cambios de STD-OKF-001 antes de publicarse.
- Cada `SKILL.md` enlaza su plantilla.

### Pendiente
- Control de cambios para `RVA`, `RTA`, `RTX` y `RRD`.
- Sustituir los marcadores de las plantillas (`<...>`, `generated.at`) al instanciarlas; el validador los rechaza en su estado actual.

## [0.2.0] - 2026-11-12

### AÃ±adido
- `scripts/check_closure.py`: validadores deterministas. Informe sin horas (C6), agenda sin decisiÃ³n pre-llenada y con Product Owner (C9), experimento con DueÃ±o, MÃ©trica y Fecha de cierre vÃ¡lida, sin marcadores sin rellenar (C5).
- `scripts/workflow.py`: control del run en `comsatel/ssp-closure/runs/<run-id>/gates.json`. La aprobaciÃ³n exige actor `human:<nombre>` y evidencia no vacÃ­a.
- `tests/test_ssp_closure.py`: 18 pruebas de validadores y control del run.
- `templates/`: agenda de Review, informe de estados, agenda de Retro y experimento como issue de GitLab.

### Pendiente
- VerificaciÃ³n del informe contra GitLab real (solo con `project_id` y acceso).

## [0.1.0] - 2026-11-12

### AÃ±adido
- Estructura inicial del plugin `ssp-closure`, segÃºn `architecture/adrs/SSP-ADR-001-ssp-closure.md` (aprobado por Ilver Anache, declaraciÃ³n).
- Orquestador `ssp-closure-orchestrator` y cinco especialistas: `review-agenda`, `review-status-report`, `retro-agenda`, `retro-experiment-tracker`, `release-readiness`.
- Decisiones de G3 incorporadas: informe sin horas (C6), aprobaciones tambiÃ©n en GitLab (C8), aceptaciÃ³n por Product Owner (C9), publicaciÃ³n de issues al cierre del pre-SSP (C10), un senior por rol (C4), formato mÃ­nimo de experimentos (C5).

### Pendiente
- Scripts, plantillas y pruebas de cada skill.
- Entrada en el catÃ¡logo de `.agents/skills/README.md` (solo aplica cuando los skills se publiquen allÃ­).
