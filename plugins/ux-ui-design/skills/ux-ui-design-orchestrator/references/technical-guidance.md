# Guía técnica — ux-ui-design-orchestrator

## Trabajo especializado
Planificar, activar skills, registrar dependencias y solicitar aprobaciones.

## Reglas de diseño
- Conservar la cadena US → UXR → FLW → SCR → prototipo → Figma gobernado → CMP/TKN → UX Handoff → Development Context Pack.
- No imponer equivalencia 1:1 entre Bounded Contexts, APIs, MicroUIs, pantallas ni módulos Flutter.
- Para cada elemento registrar ID estable, versión, origen, relaciones y estado de aprobación.
- Usar una tabla `ID | Fuente | Decisión | Evidencia | Riesgo | Estado`.
- Separar evidencia observada de propuesta; las hipótesis se marcan como hipótesis.

## Calidad del resultado
G0 alcance; G1 requerimientos; G2 pantallas; G3 sistema visual; G4 prototipo; G5 calidad; G6 handoff.

## Antipatterns
- Diseños sin casos de error, empty/loading, permisos o accesibilidad.
- Duplicación de tokens/componentes sin justificación.
- Declarar un link de Figma/Stitch/Claude Design sin que exista.
- Escribir artefactos operativos dentro de `design/ux-ui` o artefactos OKF conceptuales dentro de `comsatel`.
