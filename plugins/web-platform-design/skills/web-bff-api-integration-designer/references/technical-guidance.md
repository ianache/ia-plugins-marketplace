# Guía técnica — web-bff-api-integration-designer

## Objetivo
Diseñar BFF, contratos OpenAPI, sesión Keycloak/OAuth2 PKCE, errores, resiliencia y observabilidad.

## Fuentes y precedencia
1. Artefactos aprobados DDD (BC, Context Map, ADR) y APIs/OpenAPI.
2. UX/UI Handoff aprobado (UXR, FLW, SCR, CMP, TKN).
3. Evidencia As-Is del repositorio y decisiones técnicas aprobadas.
4. Supuestos explícitos, nunca presentados como hechos.

## Método
- Determinar escenario Greenfield, Brownfield o Evolution y aplicabilidad del skill.
- Trazar cada decisión a su fuente y registrar versión/commit cuando exista.
- Elaborar integration/bff-api-contracts.md y integration/security-integration.md si aplican, con alternativas, trade-offs y riesgos.
- Para MicroUIs evaluar BC, UX cohesion, team ownership, independent delivery, shared state, cross-context composition y costo de operación.
- Comparar con modular monolith frontend antes de recomendar partición.
- Prohibido cambiar especificaciones UX/UI o inventar aprobaciones.

## Gate
Solicitar G4 adjuntando rutas de evidencia y cuestiones abiertas; solo una persona autorizada aprueba.
