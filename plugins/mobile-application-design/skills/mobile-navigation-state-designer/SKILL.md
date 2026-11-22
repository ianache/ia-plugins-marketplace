---
name: mobile-navigation-state-designer
description: Usar cuando se requiera traducir flujos ux/ui aprobados a navegación, estados, componentes técnicos y ciclo de vida flutter en DTC-105 Mobile Flutter, bajo control del orchestrator y gates humanos.
---
# mobile-navigation-state-designer

## Propósito y límites
Traducir flujos UX/UI aprobados a navegación, estados, componentes técnicos y ciclo de vida Flutter. Diseñar, no implementar código productivo ni alterar UX/UI aprobado. Usar fuentes autorizadas; declarar ausencias, versiones y supuestos.

## Recursos propios obligatorios
- `references/contract.md`: entradas/salidas, precondiciones y dependencias.
- `references/gate-checklist.md`: criterios del gate G3.
- `references/technical-guidance.md`: decisiones técnicas y anti-patterns.
- `templates/deliverable.md`: plantilla conceptual OKF v0.2 con tipo sujeto al catálogo.
- `templates/gate-evidence.json`: evidencia estructurada de evaluación.
- `scripts/validate.py`: validación estructural del entregable (no valida contenido semántico).
- `examples/README.md`: escenario sintético y trazabilidad.
- `assets/README.md`: convenciones de diagramas y anexos.

## Entradas
UXR/FLW/SCR/CMP/TKN aprobados, arquitectura mobile, políticas de sesión. Antes de producir, verificar evidencia, fecha, versión y autorización de uso. Si falta una fuente crítica, emitir bloqueo.

## Salidas
composition/navigation-routing-spec.md; composition/state-management-spec.md; composition/ui-technical-mapping.md; composition/accessibility-implementation.md.
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
G3: rutas profundas, auth guards, lifecycle, loading/error/empty/offline states, ownership de estado y testing. Solo el responsable humano designado puede autorizarlo; el orchestrator registra la decisión.
