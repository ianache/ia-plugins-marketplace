---
type: STR
id: "STR-<period-id>"
title: "Informe de estado SSP <identificador> — <periodo>"
description: "Estado trazable de historias, pruebas, riesgos y readiness del SSP en el periodo indicado"
version: "1.0.0"
status: draft
owner: "role:delivery-manager"
classification: internal
tags: [ssp, reporting, release]
product: "<producto>"
pack: ssp-closure
skill: ssp-closure-orchestrator
related:
  - "<SSP-ID>"
generated:
  by: "ssp-closure-orchestrator/1.0.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - resource: "<referencia-export-o-query-GitLab>"
    title: "Issues del SSP"
  - resource: "<referencia-evidencia-QA>"
    title: "Evidencia de calidad y readiness"
---
# Estado del SSP <identificador> — <periodo>

## Resumen y calidad de datos

<Avance del periodo, alcance cubierto, fecha de corte, limitaciones y decisiones requeridas. No inferir datos ausentes.>

## Historias

| Estado | Historia | Criterio/observación | Issue |
|---|---|---|---|
| <estado> | <ID y título> | <dato verificable> | #<iid> |

## Casos de prueba

| Estado | Caso | Evidencia | Referencia |
|---|---|---|---|
| <estado> | <ID/título> | <ejecución/version> | <ref> |

## Preparación de release

| Señal | Estado | Evidencia | Riesgo/decisión requerida |
|---|---|---|---|
| <criterio> | <READY/NOT_READY/UNCERTAIN> | <ref> | <detalle> |

## Riesgos residuales y decisiones pendientes

- <Riesgo, defecto abierto o decisión; responsable y evidencia.>

> No incluir horas, estimados ni gasto hasta que las fuentes temporales sean completas. Cada cifra debe enlazar su fuente. Este informe informa el estado; no autoriza el despliegue.
