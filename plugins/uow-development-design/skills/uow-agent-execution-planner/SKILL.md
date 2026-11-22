---
name: uow-agent-execution-planner
description: "Usar cuando una UOW con contratos y mapa de código deba convertirse en el plan de ejecución para el agente IA del developer (pasos con prueba primero, verificación, condiciones de parada, desviaciones), con perfil neutral y perfil Claude Code con Superpowers."
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "development"
---
# UOW Agent Execution Planner
Convierte la UOW, el UCB y el UCM en el plan que sigue el agente IA del developer.
## Required
`UOW`, `UCB` y `UCM` con sus gates en PASS.
## Output
`UAP` (plantilla `templates/UAP-OKF.md`) con perfil neutral. Perfil opcional **Claude Code con Superpowers** (`resources/profiles/claude-code-superpowers.md`, plantillas `UAP-superpowers-plan.md` y `claude-code-brief.md`): plan en formato de `writing-plans` (tareas pequeñas con archivos exactos, prueba primero, comando de verificación y commit), ejecutable con `executing-plans` o `subagent-driven-development`, y las instrucciones para el `CLAUDE.md` del repositorio.
## Rules
- Cada paso lista archivos (solo dentro de `allowed_paths`), `verify` (comando) y `expected`. Un paso de implementación es siempre `test_first: true`.
- `definition_of_done` con una verificación por criterio. Condiciones de parada explícitas (contrato ambiguo, archivo fuera de límites, prueba que no puede escribirse, secreto requerido).
- `deviation_protocol`: el agente no amplía alcance ni cambia contratos; ante una desviación se detiene, la registra y escala a la persona indicada (`escalate_to`), que decide si hace falta un cambio (CHG).
- Sin secretos en el plan; solo referencias. Sin acciones destructivas ni PROD sin autorización.
- No ejecuta el desarrollo: lo hace el developer con su agente.
## Verificación determinista
`python scripts/check_uow_package.py --root <dir> --profile agent-plan --uow UOW-001` devuelve los checks `script` de `AGENT_PLAN_GATE`.
## Autorización y estado
Ejecutar solo con una autorización del orquestador verificada por el runtime. No editar `plan-status.yaml` ni `task-status.yaml`, no lanzar otros skills y no autoaprobar el gate.
## Gate proposal
Entregar `gate_proposal` con los checks de `resources/gates/AGENT_PLAN_GATE.yaml` (`{id, result, evidence_ref}`). Sin evidencia: `UNCERTAIN` o `FAIL`. El skill nunca emite `decision`/`PASS`; lo decide el orquestador. Sin PASS parcial. El `gate-report-T05.yaml` se escribe en `.comsatel/uow-development-design/runs/evidence/AGENT_PLAN_GATE/` y es lo único que este skill escribe allí.

