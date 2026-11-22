# Solution Ideation — Claude Code Plugin v1.2.1

Plugin de **innovación e ideación de soluciones** para nuevos productos y mejoras Brownfield/Evolution. Arquitectura **6 skills especializados + 1 orchestrator** con recursos completos por skill, contratos, gates y handoff hacia `requirements-engineering`.

## Instalación
Estructura nativa `.claude-plugin/plugin.json` y `skills/<name>/SKILL.md`. Cargar como plugin local de Claude Code según el mecanismo soportado por la instalación; probar discovery y activación antes de publicar en SkillVault. No se afirma validación end-to-end en Claude Code.

## Flujo
G0 Scope → G1 Opportunity Scout → G2 Problem Framing → G3 Divergent Ideation → G4 Concept Synthesis → G5 Experiments → G6 Requirements Handoff.

## Rutas
- Operativos: `.comsatel/solution-ideation/runs/<run-id>/`.
- Conceptos y propuestas OKF: `design/ideation/<run-id>/`.
- Entrega a Requirements Engineering: `SOL` en draft + `handoff.json`; Requirements produce RCP/BR/US posteriormente.

## Política OKF
`STD-OKF-001-v0.1.0-stable.md` se distribuye como estándar aprobado. Los documentos de ideación usan `SOL` (Solution Proposal, tipo aprobado en v0.1.0-stable con `ideation_stage`); una sola sigla para todas las etapas. No se crea ninguna otra sigla sin governance. Un documento de ideación solo debe usar `type: SOL` cuando represente efectivamente una propuesta de solución; las notas de brainstorming permanecen como evidencia operativa. Templates con placeholders son inválidos para publicación.

## Límites
La creatividad no equivale a novedad demostrada; un plan de experimento no equivale a validación. Gates con aprobación humana; sin merges, publicaciones ni verificaciones automáticas ficticias.

## Validación
`python scripts/validate_okf.py design/ideation/<run-id>/<documento>.md`. Requiere PyYAML. `python -m unittest discover -s tests -v` para checks locales.
