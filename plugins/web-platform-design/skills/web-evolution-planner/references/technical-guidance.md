# Guía técnica — web-evolution-planner

## Objetivo
Planificar cambios compatibles, migración, feature flags, pruebas de regresión y rollback.

## Fuentes y precedencia
1. Artefactos aprobados DDD (BC, Context Map, ADR) y APIs/OpenAPI.
2. UX/UI Handoff aprobado (UXR, FLW, SCR, CMP, TKN).
3. Evidencia As-Is del repositorio y decisiones técnicas aprobadas.
4. Supuestos explícitos, nunca presentados como hechos.

## Método
- Determinar escenario Greenfield, Brownfield o Evolution y aplicabilidad del skill.
- Trazar cada decisión a su fuente y registrar versión/commit cuando exista.
- Elaborar evolution/evolution-plan.md y evolution/rollback-plan.md si aplican, con alternativas, trade-offs y riesgos.
- Para MicroUIs evaluar BC, UX cohesion, team ownership, independent delivery, shared state, cross-context composition y costo de operación.
- Comparar con modular monolith frontend antes de recomendar partición.
- Prohibido cambiar especificaciones UX/UI o inventar aprobaciones.

## Gate
Solicitar G5 adjuntando rutas de evidencia y cuestiones abiertas; solo una persona autorizada aprueba.
