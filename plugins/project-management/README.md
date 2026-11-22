# Project Management — Claude Code Plugin v2.1.0

Un orchestrator (`mgt-delivery-orchestrator`) y seis skills especializados que gobiernan la entrega de una iniciativa, de acta a cierre, con contratos, gates humanos G0–G6 y trazabilidad. Complementa a `gsd-*` (ejecución dentro del repositorio), que se invoca como herramienta y no se duplica.

Instalación local (Claude Code): usar el directorio raíz como plugin local; manifiesto en `.claude-plugin/plugin.json`, skills en `skills/<name>/SKILL.md`.

**No** se declara validación real en Claude Code ni aprobación humana de gates. Los scripts verifican estructura, no semántica ni identidad del aprobador. Las decisiones de compromiso, cambio y cierre son siempre humanas.

## Secuencia y gates
G0 alcance -> G1 acta y roadmap `PCH`, `RMP` (`mgt-charter-roadmap-planner`) -> G2 Sprint Scope Pack `SSP` (`mgt-backlog-iteration-planner`) -> G3 publicación en GitLab (`mgt-work-publisher-synchronizer`) -> G4 riesgos y cambios `RSK`, `CHG` (`mgt-risk-change-controller`) -> G5 avance e informe `STR` (`mgt-progress-reporting-analyst`) -> G6 cierre `CLS` (`mgt-release-closure-auditor`).

Evidencia: `transition --to NEEDS_REVIEW|DONE` exige `--evidence <archivo existente>`; `approve-gate` acepta un archivo existente o una referencia verificable (URL `http(s)://…` o ID como `MR-12`, `PM-345`). El texto libre se rechaza.

Escenarios (`scripts/workflow.py init`): `initiative` (G0–G6), `iteration` (omite G1) y `cadence` (solo G4 y G5, un run por periodo). Los escenarios que omiten gates exigen `--justification`. `approve-gate` exige un actor `human:<nombre>` y evidencia.

## Herramientas que invoca (no se copian)
| Skill | Herramientas |
|---|---|
| `mgt-charter-roadmap-planner` | `development-scope-pack-builder`, `gsd-new-project`, `gsd-new-milestone` |
| `mgt-backlog-iteration-planner` | `gsd-plan-phase`, `gsd-review-backlog`; estimación propia (`estimate.py`) con los TC de `qa-design` y desarrollo con Superpowers |
| `mgt-work-publisher-synchronizer` | `gitlab-work-publisher` (issues), `report-userstory-testcase`; el Milestone y los issues (`User Story` por historia, `Proyecto` para el DSP) los gestionan los scripts propios `gitlab_milestone.py` y `gitlab_issues.py` |
| `mgt-risk-change-controller` | `gsd-health`, `gsd-forensics` |
| `mgt-progress-reporting-analyst` | `gitlab-ai-kpi-semanal`, `informe-mensual-horas-proyecto`, `gsd-progress`, `gsd-stats`, `dataviz`, `docx` |
| `mgt-release-closure-auditor` | `gsd-audit-milestone`, `gsd-ship`, `gsd-complete-milestone` |

## Relación con otros packs
Consume `business-knowledge` (BCP, BO, BCAP, BRISK), `requirements-engineering` (DSP, US, RCP, IMP), `architecture-design` (ASR, ADR) y `qa-design` (QDC). Solo GitLab como gestor de trabajo.

## Conformidad OKF
Los documentos cumplen STD-OKF-001 v0.1.0-stable. Tipos aprobados y usados aquí: `PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`. `python scripts/validate_okf.py documento.md` valida el frontmatter; `--publication` es la revisión estricta y rechaza los tipos no registrados.

## Output Pathmap v1.0.0
Ver `assets/pathmap.md` y `OUTPUT-PATH-POLICY.md`. Entregables bajo `./management/`; registros operativos en `.comsatel/project-management/runs/<run-id>/`. Validar con `scripts/validate_pathmap.py` y, para el conjunto, `skills/mgt-release-closure-auditor/scripts/check_management.py`.

Ver `COVERAGE-MATRIX.md` y `VALIDATION.md`.
