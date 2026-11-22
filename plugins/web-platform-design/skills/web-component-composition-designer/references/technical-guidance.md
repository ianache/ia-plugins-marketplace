# Guía técnica — web-component-composition-designer

## Objetivo
Mapear SCR/CMP/TKN aprobados a módulos Angular, rutas, lazy loading, estado y contratos de composición.

## Fuentes y precedencia
1. Artefactos aprobados DDD (BC, Context Map, ADR) y APIs/OpenAPI.
2. UX/UI Handoff aprobado (UXR, FLW, SCR, CMP, TKN).
3. Evidencia As-Is del repositorio y decisiones técnicas aprobadas.
4. Supuestos explícitos, nunca presentados como hechos.

## Método
- Determinar escenario Greenfield, Brownfield o Evolution y aplicabilidad del skill.
- Trazar cada decisión a su fuente y registrar versión/commit cuando exista.
- Elaborar composition/component-composition.md y composition/routing-state-design.md si aplican, con alternativas, trade-offs y riesgos.
- Para MicroUIs evaluar BC, UX cohesion, team ownership, independent delivery, shared state, cross-context composition y costo de operación.
- Comparar con modular monolith frontend antes de recomendar partición.
- Prohibido cambiar especificaciones UX/UI o inventar aprobaciones.

## Gate
Solicitar G3 adjuntando rutas de evidencia y cuestiones abiertas; solo una persona autorizada aprueba.
