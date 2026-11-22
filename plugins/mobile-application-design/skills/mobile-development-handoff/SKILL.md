---
name: mobile-development-handoff
description: Usar cuando se requiera consolidar mobile development context pack listo para implementación con agentes y qa en DTC-105 Mobile Flutter, bajo control del orchestrator y gates humanos.
---
# mobile-development-handoff

## Propósito y límites
Consolidar Mobile Development Context Pack listo para implementación con agentes y QA. Diseñar, no implementar código productivo ni alterar UX/UI aprobado. Usar fuentes autorizadas; declarar ausencias, versiones y supuestos.

## Recursos propios obligatorios
- `references/contract.md`: entradas/salidas, precondiciones y dependencias.
- `references/gate-checklist.md`: criterios del gate G6.
- `references/technical-guidance.md`: decisiones técnicas y anti-patterns.
- `templates/deliverable.md`: plantilla conceptual OKF v0.2 con tipo sujeto al catálogo.
- `templates/gate-evidence.json`: evidencia estructurada de evaluación.
- `scripts/validate.py`: validación estructural del entregable (no valida contenido semántico).
- `examples/README.md`: escenario sintético y trazabilidad.
- `assets/README.md`: convenciones de diagramas y anexos.

## Entradas
artefactos G2-G5 aprobados según escenario, UX/UI handoff, API contracts, gates. Antes de producir, verificar evidencia, fecha, versión y autorización de uso. Si falta una fuente crítica, emitir bloqueo.

## Salidas
handoff/mobile-development-context-pack.md; handoff/mobile-implementation-backlog.md; handoff/mobile-contract-traceability.md; handoff/mobile-readiness-report.md.
Todos los entregables de ingeniería van en design/mobile/<run-id>/ respetando las rutas relativas indicadas.

## Procedimiento de ejecución
1. Leer `references/contract.md`, `references/technical-guidance.md` y las fuentes verificables.
2. Validar precondiciones del gate anterior y escenario (Greenfield, Brownfield, Evolution).
3. Diseñar con referencias a BC/CTX, ADR, US, UXR/FLW/SCR, CMP/TKN, OpenAPI/FDT y commits según aplique.
4. Producir entregables con provenance, decisiones y alternativas; ejecutar `scripts/validate.py` para cada Markdown.
5. Evaluar `references/gate-checklist.md`; preparar evidencia en `templates/gate-evidence.json` sin autoaprobar.
6. Reportar rutas, riesgos, brechas y gate solicitado al orchestrator.

## Reglas de gobierno
- `.comsatel/mobile-application-design/runs/<run-id>/`: plan, estado, evidencias, aprobaciones y bloqueos.
- `design/mobile/<run-id>/`: entregables técnicos OKF v0.2; STD-OKF-001 v1.11.0-stable si está disponible en el workspace.
- Usar `type: MOB` (Mobile Application Technical Design), aprobado en STD-OKF-001 v1.11.0-stable.
- No generar ni modificar prototipos Stitch/Figma/Claude Design, pantallas visuales, Atomic Design o Design Tokens.
- No equiparar automáticamente features Mobile con MicroUIs, Bounded Contexts, microservicios o APIs.
- No inventar aprobación humana, resultados de tests, acceso a repositorios, publicación ni cumplimiento de stores.
- No almacenar tokens, credenciales o PII en los artefactos.

## Gate
G6: trazabilidad US→UX→DDD/API→Mobile→Dev/QA; acceptance criteria, riesgos y pendientes sin aprobación ficticia. Solo el responsable humano designado puede autorizarlo; el orchestrator registra la decisión.
