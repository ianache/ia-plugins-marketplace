# Contrato del skill `web-development-handoff`

**Fase:** Handoff  
**Gate:** G6  
**Objetivo:** Context Pack de desarrollo con dependencias, decisiones y criterios verificables

## Entradas
Gates previos, entregables técnicos, UX handoff y backlog. Cada fuente debe identificarse por ruta, revisión y estado de aprobación; las ausencias críticas bloquean el gate.

## Salidas
Entregable principal: `handoff/development-context-pack.md`. Para skills técnicos, ruta bajo `design/web/<run-id>/`; el orchestrator mantiene únicamente artefactos de control en `.comsatel/web-platform-design/runs/<run-id>/`.

## Contrato de entrega al siguiente skill
Registrar: `run_id`, `skill`, `version`, `source_refs`, `deliverables`, `decisions`, `assumptions`, `open_questions`, `gate_requested`, `gate_status`. Ninguna aprobación se infiere del contenido generado.

## Invariantes
- No inventar evidencia, commits, aprobaciones ni resultados de pruebas.
- No modificar artefactos UX/UI; usar únicamente el handoff aprobado.
- Los límites MicroUI se justifican con DDD + UX + ownership + despliegue; no imponer correspondencia 1:1 con API/BC.
- Los Markdown OKF siguen STD-OKF-001 v1.11.0-stable; el tipo `WEB` está aprobado en v1.11.0-stable.
