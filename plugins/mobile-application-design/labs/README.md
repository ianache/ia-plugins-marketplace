# Laboratorio sintético CL2 — Mobile Flutter

Objetivo: diseñar una app móvil de consulta de flota y telemetría, con navegación de mapa, sesiones OIDC, conectividad variable y sincronización de datos permitidos.

## Fuentes que deben proporcionarse
- BC/CTX de Flota, Vehículos, Telemetría e Identidad; decisiones ADR.
- OpenAPI de los servicios y BFF móvil; reglas de permisos y multitenancy.
- Handoff UX/UI aprobado (UXR, FLW, SCR, CMP/TKN y referencias Figma).
- Repositorio Flutter y pruebas existentes para Brownfield/Evolution.

## Criterios de revisión
1. Justificación de módulos Mobile independiente de MicroUIs y APIs.
2. Diagrama de rutas, estado y ciclo de vida.
3. Offline/cache solo donde exista requerimiento y política de datos.
4. Autenticación OAuth2/OIDC + PKCE y almacenamiento seguro.
5. Compatibilidad Android/iOS, rollout, rollback y testing.
6. G0–G6 aprobados exclusivamente por responsables humanos.

**Nota:** este laboratorio es un escenario de diseño, no una app Flutter ejecutable ni una validación E2E.
