# Web Platform Design — Plugin para Claude Code v1.2.1

Plugin nativo con `.claude-plugin/plugin.json` y siete skills auto-descubribles en `skills/<name>/SKILL.md`. Cada skill es autocontenido con `references/`, `templates/`, `scripts/`, `examples/` y `assets/`.

## Instalación
Extraer el ZIP y registrar la carpeta raíz como plugin en Claude Code mediante el mecanismo de plugins disponible en la instalación. Para pruebas locales desde la carpeta padre: `claude --plugin-dir ./web-platform-design-claude-plugin-v0.3.0` (requiere Claude Code instalado). Los nombres exactos de activación dependen del registro del plugin.

## Skills
- `web-application-reconstruction-analyzer` — Inventario verificable de Shell, MicroUIs, rutas, dependencias, APIs y deuda técnica (G1).
- `web-platform-architecture-designer` — Decisión argumentada entre frontend modular y Shell/MicroUIs, límites y despliegue (G2).
- `web-component-composition-designer` — Mapeo SCR/CMP/TKN aprobados a componentes Angular, rutas y estado (G3).
- `web-bff-api-integration-designer` — Contratos BFF, integración API, Keycloak y políticas de seguridad (G4).
- `web-evolution-planner` — Impacto, compatibilidad, rollout, rollback y migración incremental (G5).
- `web-development-handoff` — Context Pack de desarrollo con dependencias, decisiones y criterios verificables (G6).
- `web-design-orchestrator` — Plan de ejecución por escenario, dependencias y gates sin autoaprobación (G0-G6).

## Gobernanza y carpetas
`.comsatel/web-platform-design/runs/<run-id>/` contiene planes, estados, logs y evidencias operativas. `design/web/<run-id>/` contiene entregables técnicos OKF v0.2. El orchestrator no autoaprueba gates ni realiza commits.

## Limitaciones
La conformidad de cada `SKILL.md` con la estructura básica Claude Code se valida localmente. La compatibilidad runtime debe verificarse en Claude Code. Los validadores por skill son estructurales, no un validador semántico de OKF. El ZIP QA de referencia no estuvo accesible, por lo que no se afirma equivalencia exacta con ese paquete.


## v0.4.0 — Recursos completos por skill
Los siete skills contienen SKILL.md, references (contrato, gate, guía técnica), templates (OKF, entregable específico, evidencia gate), scripts (validación del entregable y de recursos), examples (inputs/outputs), assets (diagramas). Ejecutar `python scripts/validate_plugin.py`.

El tipo OKF `WEB` está aprobado en STD-OKF-001 v0.1.0-stable (Web Platform Technical Design). La validación estructural no equivale a ejecución real en Claude Code ni aprobación humana de gates.
