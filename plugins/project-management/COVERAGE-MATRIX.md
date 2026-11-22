# Matriz de cobertura

| Capacidad | Skill | Tipo | Gate | Herramienta base |
|---|---|---|---|---|
| Acta, alcance y criterios de éxito | `mgt-charter-roadmap-planner` | PCH | G1 | `development-scope-pack-builder` |
| Roadmap, hitos y dependencias | `mgt-charter-roadmap-planner` | RMP | G1 | `gsd-new-project`, `gsd-new-milestone` |
| Backlog, prioridad, DoR y Sprint Scope Pack | `mgt-backlog-iteration-planner` | SSP | G2 | `gsd-plan-phase`, `gsd-review-backlog` |
| Publicación y sincronización de issues en GitLab | `mgt-work-publisher-synchronizer` | publicación (operativo) | G3 | `gitlab-work-publisher`, `report-userstory-testcase` |
| Issues `User Story` (uno por historia del Sprint) y `Proyecto` (uno por DSP) | `mgt-work-publisher-synchronizer` | publicación (operativo) | G3 | `scripts/gitlab_issues.py` (propio) |
| Estimación de esfuerzo y costo (humano y agente, QA manual y automatizado) | `mgt-backlog-iteration-planner` | SSP (sección) | G2 | `scripts/estimate.py`, `qa-design` (TC) |
| Creación y actualización del Milestone del Sprint | `mgt-work-publisher-synchronizer` | publicación (operativo) | G3 | `scripts/gitlab_milestone.py` (propio) |
| Riesgos, dependencias y bloqueos | `mgt-risk-change-controller` | RSK | G4 | `gsd-health`, `gsd-forensics` |
| Control de cambios | `mgt-risk-change-controller` | CHG | G4 | `IMP` de requirements |
| Avance, horas, KPI e informe de estado | `mgt-progress-reporting-analyst` | STR | G5 | `gitlab-ai-kpi-semanal`, `informe-mensual-horas-proyecto`, `gsd-progress`, `gsd-stats` |
| Auditoría de hito, entrega y cierre | `mgt-release-closure-auditor` | CLS | G6 | `gsd-audit-milestone`, `gsd-ship`, `gsd-complete-milestone` |
| Planificación, gates y control del run | `mgt-delivery-orchestrator` | operativo | G0-G6 | `scripts/workflow.py` |
