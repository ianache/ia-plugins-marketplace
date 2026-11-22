# Contrato — creative-concept-explorer

**Gate:** G3. **Output:** `concept-portfolio.md`. **Schema operativo:** `gate-evidence.json`.

## Input
- initiative_id, scenario, objective, target_users, constraints, evidence_refs, preceding_gate_refs.
- Para Brownfield/Evolution: baseline existente, owners, capacidades y restricciones conocidas; si faltan, registrar gap y no asumirlas.

## Output
- `concept-portfolio.md` con `type: SOL` cuando exista propuesta conceptual; mantener investigación cruda/brainstorming en `.comsatel/solution-ideation/runs/<run-id>/`.
- `gate-evidence.json`: skill, gate, outcome, evidence_paths, issues, reviewer, approved (inicialmente false).
- Referencias de trazabilidad: oportunidad → problema → ideas → concepto → hipótesis → decisión → handoff.

## Regla de encadenamiento
No consumir un output como aprobado por mera existencia de archivo. Verificar aprobación humana y referencias antes de iniciar el siguiente skill.
