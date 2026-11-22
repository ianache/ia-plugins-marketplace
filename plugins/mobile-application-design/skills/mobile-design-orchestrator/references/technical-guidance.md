# Guía técnica — mobile-design-orchestrator

## Decisiones
secuenciación condicionada, evidencia de outputs, gates humanos, bloqueo por dependencias y reporte final.

## Arquitectura Flutter
- Preferir módulos por capacidad de producto y cohesive features, no una capa por pantalla.
- Separar presentation, application/domain y data/infrastructure cuando aporta testabilidad; justificar packages separados.
- Respetar APIs contract-first y BFF; evitar reglas de dominio duplicadas en el cliente.
- Offline-first solo cuando haya requisitos explícitos; documentar fuente de verdad, conflictos, cifrado, retención y reconciliación.
- Para OAuth2/OIDC en móvil, evaluar Authorization Code + PKCE, system browser, secure storage y expiración de sesión.
- Distinguir comportamiento Android/iOS, deep links, permisos, background execution y políticas de store.
- Validar trazabilidad hacia el handoff UX/UI aprobado; solicitar change request ante discrepancias.
