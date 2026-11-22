---
name: release-readiness
description: Evaluar evidencia de QA, defectos abiertos y riesgos residuales de un SSP para aportar readiness al informe STR del periodo sin decidir el despliegue.
metadata:
  version: "0.1.0"
  author: "COMSATEL"
  type: "specialist"
---

# Release Readiness

## Activación y alcance

Invocar cuando se solicite valorar readiness de un incremento antes de release. El skill resume evidencia, no autoriza publicación ni despliegue.

## Entradas

SSP/periodo, resultados de prueba, ejecuciones, defectos abiertos/cerrados, `qa-design:qa-quality-intelligence` cuando exista, fuentes y decisiones de aceptación pendientes.

## Procedimiento

1. Inventariar evidencia disponible con versión/fecha y referencia.
2. Distinguir resultado observado, ausencia de evidencia, defecto abierto y riesgo aceptado.
3. Asignar `READY`, `NOT_READY` o `UNCERTAIN` de acuerdo con criterios de QA disponibles; sin evidencia de prueba no usar READY.
4. Guardar payload sin frontmatter en `.comsatel/ssp-closure/runs/<run-id>/task-results/T5/release-readiness.json`.
5. Proponer `RELEASE_READINESS_GATE`; aportar campos al `STR` de periodo sin generar un documento RRD.

## Salida y gate

Payload operativo para consolidar en el `STR` existente del periodo. No hay tipo `RRD` en STD-OKF-001 v1.9.0. La aprobación de calidad y la decisión de despliegue corresponden a personas autorizadas.

## Restricciones

No omitir defectos, no inferir aceptación de riesgo, no desplegar y no afirmar disponibilidad de integración no ejecutada. Usar `templates/readiness-payload.json`.
