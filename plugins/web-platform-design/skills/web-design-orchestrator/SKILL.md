---
name: web-design-orchestrator
description: Coordina seis skills de diseño técnico Web (Angular Shell MicroUIs BFF), escenarios Greenfield Brownfield Evolution, dependencias, gates y handoff, sin asumir responsabilidades UX/UI.
metadata:
  version: "0.1.0"
---
# Web Design Orchestrator

1. Registrar `scenario`, producto, aplicación, repositorio, commit, ADR, ASR, APIs, FDT y fuentes UX/UI en `.comsatel/web-platform-design/runs/<run-id>/scope-manifest.yaml`.
2. Ejecutar `python scripts/workflow.py init --workspace <ruta> --run-id <id> --scenario <greenfield|brownfield|evolution>`; `init` crea `scope-manifest.yaml`, `state.json` y `execution-plan.yaml`. Completar `sources` en el manifiesto (y vaciar `missing_sources`) antes de `approve --gate G0 --actor human:<nombre> --evidence <ref>`; G0 se rechaza sin fuentes. El `--scenario` no distingue mayúsculas.
3. Despachar únicamente tareas elegibles por dependencias: Greenfield omite reconstrucción y evolución; Brownfield reconstruye As-Is y puede detenerse con documentación técnica y handoff; Evolution reconstruye As-Is y produce plan de migración.
4. Solicitar a cada skill resultados en `design/web/<run-id>/`; mantener plan, estados, aprobaciones y evidencia en `.comsatel/web-platform-design/runs/<run-id>/`.
5. Gates: G0 alcance/fuentes; G1 As-Is (si aplica); G2 arquitectura Shell/MicroUI; G3 mapping UX/UI y state/routing; G4 BFF/API/security; G5 evolution (si aplica); G6 handoff listo. Nunca autoaprobar gates. Registrar actor, fecha y evidencia de cada aprobación.
6. Antes de G6 verificar que UX/UI Design Handoff sea aprobado y trazable o registrar bloqueo; en Brownfield de solo documentación se puede declarar handoff técnico As-Is con alcance limitado, sin afirmar UX aprobado.
7. Handoff final a KB `codebase/<WEB_APP>/` y repositorio de código exclusivamente mediante MR y aprobaciones externas. No modificar fuentes UX/UI, no fusionar cambios automáticamente.
8. Validar Markdown conceptual contra STD-OKF-001 v0.1.0-stable y revisar contratos OpenAPI/FDT externos sin modificarlos silenciosamente.

## Separación obligatoria de carpetas
Toda planificación, task ledger, gate register, evidence log, decisiones operativas y estado de ejecución se escribe exclusivamente en `.comsatel/web-platform-design/runs/<run-id>/`. Los entregables especializados, principalmente OKF v0.2, se escriben en `design/web/<run-id>/`. No guardar documentos operativos en design/web ni entregables conceptuales en comsatel.

## Regla de delimitación de MicroUIs
Consumir BC, CTX, AGG, capacidades de dominio, catálogo de APIs/OpenAPI y FDT; proponer una matriz `MicroUI × Bounded Context × API × User Flow × owner × deployment`. Los BC son una restricción arquitectónica y no una equivalencia 1:1. Justificar cada MicroUI mediante cohesión de experiencia, ownership, autonomía de despliegue, navegación, cambios coordinados, seguridad y rendimiento. Documentar tradeoffs, cross-context composition y excepciones en ADR cuando corresponda. Gate G2 bloquea divisiones sin justificación y exige revisión humana.

## Cuándo activar este skill
Activa este skill cuando el orchestrator lo seleccione para su tarea especializada y las dependencias estén aprobadas. No ejecutar cambios en repositorios ni publicar sin autorización humana.

## Contrato de ejecución Claude Code
- Lee las fuentes autorizadas desde el workspace y cita sus rutas, commit o versión. No inventes evidencias ni decisiones aprobadas.
- Produce los artefactos de ingeniería en `design/web/<run-id>/` y no escribas allí estado de ejecución.
- Conserva planes, registro de gates, decisiones operativas y trazas en `.comsatel/web-platform-design/runs/<run-id>/`.
- Si faltan contratos de UX/UI, DDD, OpenAPI o FDT requeridos, registra la brecha y solicita resolución; no reconstruyas UX/UI desde suposiciones.
- Los Markdown conceptuales deben ajustarse a Google OKF v0.2 y STD-OKF-001 v0.1.0-stable; usar solo tipos registrados en el estándar (`WEB` está aprobado en v0.1.0-stable).
- Devuelve un resumen con archivos generados, fuentes utilizadas, riesgos, bloqueos y gate solicitado.

## Recursos obligatorios del skill (Claude Code)
- `references/technical-guidance.md`: método especializado y criterios técnicos.
- `templates/deliverable-specific.md`: estructura de salida especializada; `type: WEB` (aprobado en STD-OKF-001 v0.1.0-stable).
- `templates/gate-evidence.json`: contrato de evidencia, pendiente de aprobación humana.
- `examples/sample-input.json` y `examples/sample-output.json`: contratos de ejemplo, no evidencia real.
- `assets/diagram-conventions.md`: convenciones de diagramas editables.
- `scripts/validate_resources.py`: verificación de integridad de recursos.
Leer los recursos especializados antes de generar entregables; no limitarse al `SKILL.md`.
