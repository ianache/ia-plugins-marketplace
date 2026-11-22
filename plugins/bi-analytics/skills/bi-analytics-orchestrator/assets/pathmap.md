# BI Analytics - Output pathmap v2.0.0

Directorio base del workspace donde se invoca el plugin. Las rutas son relativas a esa raíz.

| Tipo | Directorio | Skill productor | Gate | Plantilla |
|---|---|---|---|---|
| BIC | `./bi/context/` | bi-decision-context-analyst | G1 | `skills/bi-decision-context-analyst/assets/artifact.md` |
| KPI | `./bi/kpis/` | bi-kpi-definition-designer | G2 | `skills/bi-kpi-definition-designer/assets/artifact.md` |
| CTLG | `./bi/kpis/` | bi-kpi-definition-designer | G2 | `skills/bi-kpi-definition-designer/assets/catalog.md` |
| DSM | `./bi/sources/` | bi-data-source-mapper | G3 | `skills/bi-data-source-mapper/assets/artifact.md` |
| DMD | `./bi/model/` | bi-dimensional-model-designer | G4 | `skills/bi-dimensional-model-designer/assets/artifact.md` |
| DSH | `./bi/dashboards/` | bi-dashboard-report-designer | G5 | `skills/bi-dashboard-report-designer/assets/artifact.md` |
| BIQ | `./bi/governance/` | bi-quality-governance-validator | G6 | `skills/bi-quality-governance-validator/assets/artifact.md` |

Las salidas conceptuales usan la plantilla de su tipo. El BIQ de dominio lo produce `bi-quality-governance-validator` en `./bi/governance/`. El orchestrator guarda un resumen operativo sin tipo OKF en `.comsatel/bi-analytics/runs/<run-id>/run-summary.md`, usando `skills/bi-analytics-orchestrator/assets/run-summary-template.md`.

## Estado de gestion del orchestrator

Raiz por run: `.comsatel/bi-analytics/runs/<run-id>/`. El orchestrator registra aqui `plan.yaml`, `plan-status.yaml`, `tasks/<task-id>/task-status.yaml`, `evidence/<gate-id>/` y `run-summary.md`. El run ID se registra en el plan y no se sobrescribe al reanudar. Los especialistas escriben entregables de dominio bajo `./bi/` segun la tabla anterior.

## Reglas
1. Prefijo del archivo = `id` del frontmatter (`BI-<TIPO>-NNN-<slug>.md`). Un CTLG es un único documento por producto (`BI-CTLG-001-<slug>.md`).
2. El `type` del frontmatter debe ser una sigla de esta tabla; un tipo desconocido bloquea el gate.
3. Estado operativo del orquestador en `.comsatel/bi-analytics/runs/<run-id>/`; los entregables y documentos OKF solo en sus destinos canonicos bajo `./bi/`.
4. Solo una instrucción explícita del usuario permite cambiar una ruta; se registra en el run.
5. No sobrescribir un entregable existente sin decisión explícita de evolución; preservar IDs y links.
6. Entradas externas (TRM, BR, IMD de `business-knowledge`) se leen y no se modifican.
