# Contrato del skill `web-component-composition-designer`

**Fase:** Composition  
**Gate:** G3  
**Objetivo:** Mapeo SCR/CMP/TKN aprobados a componentes Angular, rutas y estado

## Entradas
UX handoff aprobado, arquitectura G2, SCR, CMP, TKN. Cada fuente debe identificarse por ruta, revisión y estado de aprobación; las ausencias críticas bloquean el gate.

## Salidas
Entregable principal: `composition/component-composition.md`. Para skills técnicos, ruta bajo `design/web/<run-id>/`; el orchestrator mantiene únicamente artefactos de control en `.comsatel/web-platform-design/runs/<run-id>/`.

## Contrato de entrega al siguiente skill
Registrar: `run_id`, `skill`, `version`, `source_refs`, `deliverables`, `decisions`, `assumptions`, `open_questions`, `gate_requested`, `gate_status`. Ninguna aprobación se infiere del contenido generado.

## Invariantes
- No inventar evidencia, commits, aprobaciones ni resultados de pruebas.
- No modificar artefactos UX/UI; usar únicamente el handoff aprobado.
- Los límites MicroUI se justifican con DDD + UX + ownership + despliegue; no imponer correspondencia 1:1 con API/BC.
- Los Markdown OKF siguen STD-OKF-001 v0.1.0-stable; el tipo `WEB` está aprobado en v0.1.0-stable.
