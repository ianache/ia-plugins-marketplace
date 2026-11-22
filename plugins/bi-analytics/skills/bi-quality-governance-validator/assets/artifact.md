---
type: BIQ
title: "BI Quality and Governance Report — <alcance>"
description: "<una frase: resultado de la validación de trazabilidad, calidad y gobierno de la línea base>"
id: BI-BIQ-000
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-quality-governance-validator
tags: [bi, analytics, governance]
generated:
  by: bi-quality-governance-validator/1.0.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<URI o ruta de los entregables validados>"
    title: "<título>"
related: ["BI-BIC-000", "BI-KPI-000", "BI-DSM-000", "BI-DMD-000", "BI-DSH-000"]
---
# BI Quality and Governance Report — <alcance>

> **Definición:** resultado de validar la línea base de BI completa (BIC, KPI, DSM, DMD y DSH): trazabilidad, huérfanos, calidad de datos, gobierno y acceso, y handoff.
> **Regla:** PASS exige evidencia verificable por criterio. La existencia de archivos no basta. La aprobación de G6 la da una persona autorizada.

## 1. Alcance validado
> **Contenido mínimo:** lista de entregables con su ID y versión, y los modos de ejecución aplicados (GREENFIELD, BROWNFIELD o EVOLUTION).

| Entregable | ID | Versión | Modo |
|---|---|---|---|
| BIC | BI-BIC-000 | | |
| KPI | BI-KPI-000 | | |
| DSM | BI-DSM-000 | | |
| DMD | BI-DMD-000 | | |
| DSH | BI-DSH-000 | | |

## 2. Matriz de trazabilidad
> **Definición:** cadena BIC → KPI → medida (DMD) → fuente (DSM) → visualización (DSH).
> **Contenido mínimo:** una fila por KPI con cada eslabón referenciado por ID. Un eslabón vacío es un hueco.

| Decisión (BIC) | KPI | Medida (DMD) | Fuente (DSM) | Visualización (DSH) |
|---|---|---|---|---|
| D-01 | KPI-NNN | | S-01 | P-01 |

## 3. Huérfanos
> **Definición:** elementos que no se conectan con la cadena en alguna dirección.
> **Contenido mínimo:** por cada huérfano, tipo, ID, dirección del hueco y si bloquea G6.

| Tipo | ID | Hueco | Bloquea G6 |
|---|---|---|---|
| | | | |

## 4. Calidad de datos
> **Definición:** controles de calidad previstos y su evidencia.
> **Contenido mínimo:** por control, fuente, dimensión, estado y referencia a la evidencia. Sin evidencia, el estado es «Sin evidencia».

| Fuente | Control | Dimensión | Estado | Evidencia |
|---|---|---|---|---|
| S-01 | | | Sin evidencia | |

## 5. Gobierno y acceso
> **Definición:** owners, clasificación de datos y control de acceso de los entregables.
> **Contenido mínimo:** owner asignado a cada entregable, clasificación de datos y revisión de acceso por rol.

## 6. Veredictos por criterio
> **Definición:** resultado de cada criterio de G6.
> **Contenido mínimo:** criterio, veredicto (PASS, FAIL o BLOCKED) y evidencia. Un criterio sin evidencia no puede ser PASS.

| Criterio | Veredicto | Evidencia |
|---|---|---|
| Trazabilidad completa sin huérfanos | | |
| Calidad de datos documentada | | |
| Control de acceso documentado | | |
| Frontmatter OKF válido en todos los entregables | | |

## 7. Riesgos y decisiones humanas pendientes
> **Contenido mínimo:** riesgo o decisión, impacto, responsable y referencia al veredicto que lo origina.

## 8. Handoff
> **Definición:** resumen para quien aprueba G6.
> **Contenido mínimo:** alcance, veredicto global, riesgos abiertos y estado «Pendiente de aprobación humana». Este documento no se marca aprobado por el skill.

## 9. Validación
- [ ] Todos los entregables listados con ID y versión
- [ ] Cada KPI tiene la cadena de trazabilidad completa o hueco reportado
- [ ] Cada criterio tiene veredicto y evidencia
- [ ] Huérfanos que bloquean G6 identificados
- [ ] Handoff marcado pendiente de aprobación humana
