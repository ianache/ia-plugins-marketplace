# Guía técnica — ui-screen-specification-designer

## Trabajo especializado
Derivar scr, interacciones, validaciones, accesibilidad preliminar y estados de pantalla.

## Reglas de diseño
- Conservar la cadena US → UXR → FLW → SCR → prototipo → Figma gobernado → CMP/TKN → UX Handoff → Development Context Pack.
- No imponer equivalencia 1:1 entre Bounded Contexts, APIs, MicroUIs, pantallas ni módulos Flutter.
- Para cada elemento registrar ID estable, versión, origen, relaciones y estado de aprobación.
- Usar una tabla `ID | Fuente | Decisión | Evidencia | Riesgo | Estado`.
- Separar evidencia observada de propuesta; las hipótesis se marcan como hipótesis.

## Calidad del resultado
SCR vinculadas a FLW, loading/empty/error, permisos y responsive.

## Antipatterns
- Diseños sin casos de error, empty/loading, permisos o accesibilidad.
- Duplicación de tokens/componentes sin justificación.
- Declarar un link de Figma/Stitch/Claude Design sin que exista.
- Escribir artefactos operativos dentro de `design/ux-ui` o artefactos OKF conceptuales dentro de `comsatel`.
