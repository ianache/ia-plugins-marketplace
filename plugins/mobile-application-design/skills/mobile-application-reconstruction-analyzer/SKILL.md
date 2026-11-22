---
name: mobile-application-reconstruction-analyzer
description: Usar cuando se requiera reconstruir arquitectura as-is flutter, dependencias, navegación, integración, almacenamiento y deuda técnica en DTC-105 Mobile Flutter, bajo control del orchestrator y gates humanos.
---
# mobile-application-reconstruction-analyzer

## Propósito y límites
Reconstruir arquitectura As-Is Flutter, dependencias, navegación, integración, almacenamiento y deuda técnica. Diseñar, no implementar código productivo ni alterar UX/UI aprobado. Usar fuentes autorizadas; declarar ausencias, versiones y supuestos.

## Recursos propios obligatorios
- `references/contract.md`: entradas/salidas, precondiciones y dependencias.
- `references/gate-checklist.md`: criterios del gate G1.
- `references/technical-guidance.md`: decisiones técnicas y anti-patterns.
- `templates/deliverable.md`: plantilla conceptual OKF v0.2 con tipo sujeto al catálogo.
- `templates/gate-evidence.json`: evidencia estructurada de evaluación.
- `scripts/validate.py`: validación estructural del entregable (no valida contenido semántico).
- `examples/README.md`: escenario sintético y trazabilidad.
- `assets/README.md`: convenciones de diagramas y anexos.

## Entradas
repositorio Flutter, versiones/commit, ADR, APIs y documentación vigente. Antes de producir, verificar evidencia, fecha, versión y autorización de uso. Si falta una fuente crítica, emitir bloqueo.

## Salidas
as-is/mobile-as-is-assessment.md; as-is/mobile-dependency-inventory.md; as-is/mobile-risk-register.md.
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
G1: inventario con evidencia por ruta, versión y confianza; riesgos sin inferir código inexistente. Solo el responsable humano designado puede autorizarlo; el orchestrator registra la decisión.
