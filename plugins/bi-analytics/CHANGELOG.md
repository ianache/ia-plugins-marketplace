# Changelog

## [2.0.0] - 2026-11-15

### Changed
- Breaking: orchestrator management files now live per run at `.comsatel/bi-analytics/runs/<run-id>/`; updated workflow, pathmap, gate evidence policy and runtime example.
- The orchestrator gate report is an operational `run-summary.md` without OKF metadata. The domain BIQ remains owned by `bi-quality-governance-validator` and is stored at `./bi/governance/`.
- Bumped plugin major version for the output-path contract change.

### Migration
- Move each existing `./comsatel/bi-analytics/` state tree into `.comsatel/bi-analytics/runs/<run-id>/`; assign a stable run ID and preserve the plan, task statuses and evidence.


## [1.4.0] - 2026-11-07

### Cambiado

- Propagación de STD-OKF-001 v1.8.0-stable (tipo `BSN`, ampliación aditiva): copia del estándar, referencias a la versión y lista de tipos aprobados de los validadores. Sin cambios de contrato de skills.

## [1.3.1] - 2026-11-07

### Corregido

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md`: erratum del tipo `TRM`. El catálogo de términos es `business/terms/CTLG-TRM.md` (tipo `CTLG`), no `business/terms/index.md`. Corrección textual; sin cambios de contrato.


## [1.3.0] - 2026-11-07

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.7.0-stable.md` (ampliación v1.7.0: tipo `EPC`, aprobado el 2026-11-07). Lista de tipos aprobados del validador regenerada desde la maestra. Sin cambios de contrato en los skills.

## [1.2.0] - 2026-10-31

### Añadido

- Tipo documental común `CTLG` (Catálogo): índice de elementos de un mismo tipo, enlazado a sus documentos de definición. Cada skill define su plantilla de contenido. Propuesto en el maestro del estándar; pendiente de aprobación (no propagado a las copias de `STD-OKF-001`).
- Plantilla `skills/bi-kpi-definition-designer/assets/catalog.md` para el catálogo de KPI (`BI-CTLG-001`).

### Cambiado

- `bi-kpi-definition-designer` (1.2.0): un documento `BI-KPI-NNN` por KPI con su definición completa, y un catálogo `BI-CTLG-001` ordenado alfabéticamente. El catálogo solo copia nombre oficial, código, estado y versión de cada KPI, y no repite la definición.
- Salidas del skill `bi-kpi-definition-designer`: pasa de un único documento a varios (`KPI` por indicador y `CTLG`). Según AGENTS.md, este cambio de tipo y salidas corresponde a MAJOR; se publica como 1.2.0 por decisión explícita del responsable.
- Pathmap y orquestador: fila `CTLG` (`./bi/kpis/`) y tarea T-02 con salidas `KPI, CTLG`.

## [1.1.0] - 2026-10-31

### Cambiado

- Copia de STD-OKF-001 sincronizada con la maestra `STD-OKF-001-v1.5.0-stable.md`. Sin cambios de contrato en los skills.
- Lista de tipos aprobados del validador generada desde la maestra; incluye los tipos de las ampliaciones v1.4.0 y v1.5.0.

## 1.0.0
- Pack inicial de Business Intelligence y analítica: un orchestrator y seis especialistas.
- Catálogo de tipos `BIC`, `KPI`, `DSM`, `DMD`, `DSH`, `BIQ`.
- Gates G0-G6 con política `CONDITIONAL_HIL` (G1-G5) y `MANDATORY_HIL` (G0, G6).
- Modos `GREENFIELD`, `BROWNFIELD`, `EVOLUTION`.
- Estructura basada en `business-knowledge`, con `pack.yaml`, runtime de ejemplo y recursos del estándar.
- Comportamiento por modo (GREENFIELD, BROWNFIELD, EVOLUTION) en el orquestador y en cada especialista; `artifact_action` en el plan de ejemplo.
- Plantilla por tipo documental (`assets/artifact.md`) con estructura, definición y contenido mínimo por sección.
- STD-OKF-001 del pack en v1.1.0: catálogo de los seis tipos (BIC, KPI, DSM, DMD, DSH, BIQ) y reglas de plantilla.
