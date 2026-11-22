---
name: web-evolution-planner
description: Usar para diseñar evolución y compatibilidad en el diseño técnico de plataformas Web Angular Shell y MicroUIs; produce artefactos trazables bajo design/web y no altera UX/UI.
---
# web-evolution-planner

## Recursos del skill
- `references/contract.md`: contrato versionado, dependencias y criterios de aceptación.
- `references/gate-checklist.md`: checklist de revisión humana.
- `templates/deliverable.md`: plantilla OKF orientativa (tipo sujeto a catálogo aprobado).
- `scripts/validate.py`: verificador estructural local, no reemplaza aprobación.
- `examples/README.md`: ejemplo de invocación y evidencias.
- `assets/README.md`: convenciones para diagramas y recursos del skill.

## Propósito
Diseñar evolución y compatibilidad. Separar diseño técnico Web del diseño UX/UI, que pertenece a otro plugin.

## Entradas requeridas
As-Is/To-Be, contratos, dependencias, NFR, UX/UI cambios aprobados. Validar existencia y versiones; si falta una fuente crítica, registrar bloqueo, nunca inventar evidencias.

## Salidas obligatorias
evolution/impact-analysis.md; evolution/migration-plan.md; evolution/rollback-plan.md; evolution/compatibility-matrix.yaml.

Escribir **solo** dentro de `design/web/<run-id>/`, manteniendo subcarpetas indicadas. Cada Markdown conceptual debe cumplir STD-OKF-001 v1.11.0-stable (Google OKF v0.2), con `type`, `id`, `version`, `status`, `generated`, `sources`, `pack`, `skill` y enlaces trazables. Si el tipo no está registrado, solicitar aprobación para ampliarlo; no etiquetar falsamente como API/FDT/ADR.

## Procedimiento
1. Leer el manifiesto de alcance y la evidencia disponible, y distinguir hechos de supuestos.
2. Producir los artefactos con referencias explícitas a US, UXR, FLW, SCR, CMP, TKN, BC, OpenAPI, FDT y ADR cuando correspondan.
3. Validar consistencia de arquitectura, seguridad, tenancy, performance, accesibilidad implementable, observabilidad y contratos aplicables.
4. Emitir evidencia y asuntos abiertos; entregar al orchestrator para gate **G5**. No autoaprobar gates ni publicar a KB.

## Restricciones
- No crear ni modificar wireframes, prototipos, componentes visuales ni Design Tokens; consumir el handoff UX/UI aprobado.
- No inferir un MicroUI por cada pantalla ni un Bounded Context por cada MicroUI.
- No colocar reglas de dominio en Shell ni en BFF; las adaptaciones BFF deben justificarse.
- No inventar validaciones de Figma, GitLab, repositorio ni identidad humana.

## Contrato de límites MicroUI
Consultar Bounded Contexts y Context Map del DDD Pack, APIs/OpenAPI/FDT y flujos UX/UI para identificar dependencias. No imponer correspondencia 1:1 entre MicroUI, BC, API, microservicio o pantalla. Registrar mapping, ownership, cohesión de UX, autonomía de despliegue, integración cross-context y decisiones de partición; escalar excepciones al gate de arquitectura G2.

## Cuándo activar este skill
Activa este skill cuando el orchestrator lo seleccione para su tarea especializada y las dependencias estén aprobadas. No ejecutar cambios en repositorios ni publicar sin autorización humana.

## Contrato de ejecución Claude Code
- Lee las fuentes autorizadas desde el workspace y cita sus rutas, commit o versión. No inventes evidencias ni decisiones aprobadas.
- Produce los artefactos de ingeniería en `design/web/<run-id>/` y no escribas allí estado de ejecución.
- Conserva planes, registro de gates, decisiones operativas y trazas en `.comsatel/web-platform-design/runs/<run-id>/`.
- Si faltan contratos de UX/UI, DDD, OpenAPI o FDT requeridos, registra la brecha y solicita resolución; no reconstruyas UX/UI desde suposiciones.
- Los Markdown conceptuales deben ajustarse a Google OKF v0.2 y STD-OKF-001 v1.11.0-stable; usar solo tipos registrados en el estándar (`WEB` está aprobado en v1.11.0-stable).
- Devuelve un resumen con archivos generados, fuentes utilizadas, riesgos, bloqueos y gate solicitado.

## Recursos obligatorios del skill (Claude Code)
- `references/technical-guidance.md`: método especializado y criterios técnicos.
- `templates/deliverable-specific.md`: estructura de salida especializada; `type: WEB` (aprobado en STD-OKF-001 v1.11.0-stable).
- `templates/gate-evidence.json`: contrato de evidencia, pendiente de aprobación humana.
- `examples/sample-input.json` y `examples/sample-output.json`: contratos de ejemplo, no evidencia real.
- `assets/diagram-conventions.md`: convenciones de diagramas editables.
- `scripts/validate_resources.py`: verificación de integridad de recursos.
Leer los recursos especializados antes de generar entregables; no limitarse al `SKILL.md`.
