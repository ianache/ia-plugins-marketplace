# Laboratorio WEB-CL2-001 — Shell, MicroUIs y BFF

**Tipo:** caso sintético de arquitectura para ejercitar los contratos; no representa arquitectura validada de CL2 ni ejecución real en Angular/Claude Code.

## Entradas simuladas
- Bounded Contexts: Distributor Management, Identity & Access, Vehicle Management, Telemetry.
- Experiencias: Administración de distribuidores; Monitoreo de flota.
- Interfaces: UX-HOF-001 (simulado); OpenAPI-Distributor, OpenAPI-Identity, OpenAPI-Vehicle, OpenAPI-Telemetry (referencias ficticias, no contratos publicados).

## Hipótesis a evaluar en G2
- Shell: sesión y navegación global, carga de MicroUIs, sin reglas de negocio.
- MicroUI Distribuidores: experiencia cohesiva que consume capacidades de Distributor Management e Identity & Access a través de BFF autorizado.
- MicroUI Monitoreo: experiencia que integra Vehicle Management y Telemetry.
- Alternativa obligatoria: monolito frontend modular frente a MicroUIs desplegables independientemente.
- Ninguna partición implica relación 1:1 MicroUI/BC/API.

## Secuencia del laboratorio
1. Inicializar escenario `greenfield` y comprobar carpetas `comsatel/` y `design/web/`.
2. Validar G0 mediante aprobación humana externa; registrar únicamente la referencia verificable en CLI.
3. Ejecutar `web-platform-architecture-designer` con BC, CTX, UX handoff y API contracts reales antes de producir una decisión final.
4. Completar matriz de delimitación: experiencia, BC consultados, API, ownership, autonomía, alternativas y tradeoffs.
5. Revisar G2 con arquitecto; no aprobar automáticamente.
6. Continuar composición, BFF/API y handoff únicamente tras gates aprobados.

## Criterios de aceptación
- El run operativo está exclusivamente bajo `.comsatel/web-platform-design/runs/<run-id>/`.
- Los documentos de diseño están exclusivamente bajo `design/web/<run-id>/`.
- Se detectan dependencias UX/UI y DDD ausentes como bloqueos, no se inventan.
- Se compara MicroUIs versus frontend modular, con tradeoffs y decisión registrada.
- G2 exige evidencia de la matriz y aprobación humana externa.
- No se afirma que las APIs ni el diseño UX/UI simulado estén aprobados.

## Limitación
Este paquete contiene un **laboratorio de contrato y workflow**, no una aplicación Angular ejecutable, un BFF ni validación end-to-end en repositorios de producto.
