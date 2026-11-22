# BI Analytics - Claude Code Plugin v2.0.0

Un orchestrator (`bi-analytics-orchestrator`) y seis skills especializados que construyen la línea base de Business Intelligence y analítica de un producto o iniciativa: contexto de decisiones, KPI, fuentes de datos, modelo dimensional, dashboards e informes, y calidad y gobierno. Sigue la práctica "1 orchestrator + máximo 6 especialistas" del estándar COMSATEL y reutiliza la estructura de `business-knowledge`.

Instalación desde el catálogo (Claude Code):

```text
/plugin install bi-analytics@comsatel-skills-catalog
```

Instalación local: usar el directorio raíz como plugin local; manifiesto en `.claude-plugin/plugin.json`, skills en `skills/<name>/SKILL.md`.

**No** se declara validación real en Claude Code ni aprobación humana de gates. Los scripts verifican estructura, no la semántica de los entregables.

## Secuencia y gates

G0 alcance y fuentes -> G1 contexto de decisiones `BIC` (`bi-decision-context-analyst`) -> G2 KPI `KPI` y catálogo `CTLG` (`bi-kpi-definition-designer`) y G3 fuentes `DSM` (`bi-data-source-mapper`), independientes entre sí -> G4 modelo dimensional `DMD` (`bi-dimensional-model-designer`) -> G5 dashboards e informes `DSH` (`bi-dashboard-report-designer`) -> G6 calidad, gobierno y handoff `BIQ` (`bi-quality-governance-validator`).

| Gate | Política | Tarea | Tipo |
|---|---|---|---|
| G0 | MANDATORY_HIL | — | — |
| G1 | CONDITIONAL_HIL | T-01 | BIC |
| G2 | CONDITIONAL_HIL | T-02 | KPI, CTLG |
| G3 | CONDITIONAL_HIL | T-03 | DSM |
| G4 | CONDITIONAL_HIL | T-04 | DMD |
| G5 | CONDITIONAL_HIL | T-05 | DSH |
| G6 | MANDATORY_HIL | T-06 | BIQ |

Modos soportados: `GREENFIELD`, `BROWNFIELD`, `EVOLUTION`. El modo es el escenario; `artifact_action` (`CREATE`, `UPDATE`, `NO_CHANGE`, `BLOCKED`) es independiente.

## Rutas
- Entregables: `./bi/context/`, `./bi/kpis/`, `./bi/sources/`, `./bi/model/`, `./bi/dashboards/`, `./bi/governance/` (ver `skills/bi-analytics-orchestrator/assets/pathmap.md`).
- Estado operativo por ejecucion: `.comsatel/bi-analytics/runs/<run-id>/` (`plan.yaml`, `plan-status.yaml`, `tasks/<task-id>/task-status.yaml`, `evidence/` y `run-summary.md`). El resumen es operativo, no OKF. Ejemplo en `runtime-example/.comsatel/bi-analytics/runs/example-run/`.

## Entradas externas
TRM, BR e IMD de `business-knowledge` se leen cuando existen; este pack no los modifica.

## Limitaciones
- No se portan `workflow.py` ni `validate_okf.py` del plugin `business-knowledge`: el control de gates y la validación OKF dependen del host y del indexador de la organización.
- El catálogo de siglas (`BIC`, `KPI`, `CTLG`, `DSM`, `DMD`, `DSH`, `BIQ`) es propuesto y debe conciliarse con el catálogo de la organización antes de publicar.
- `scripts/gate_governance.py` de la fábrica no se copia; la política está en `assets/gate-policy.example.yaml`.

Estándar de nombres y objetos del modelo dimensional: [`resources/fact-dim-modelling-standard.md`](resources/fact-dim-modelling-standard.md). El skill `bi-dimensional-model-designer` lo aplica en cada DMD.
