---
type: DSH
title: "Dashboard and Report Specification — <alcance>"
description: "<una frase: pantallas e informes para las audiencias del alcance>"
id: BI-DSH-000
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-dashboard-report-designer
tags: [bi, analytics, dashboard]
generated:
  by: bi-dashboard-report-designer/1.0.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<URI o ruta del catálogo de KPI>"
    title: "<título>"
related: ["BI-KPI-000", "BI-DMD-000", "BI-BIC-000"]
---
# Dashboard and Report Specification — <alcance>

> **Definición:** especificación de las pantallas e informes que consumen las audiencias, con los KPI que muestra cada una, sus filtros, sus niveles de detalle y su control de acceso.
> **Regla:** toda visualización referencia un KPI o una medida del catálogo. No se crean métricas nuevas aquí.

## 1. Propósito y audiencia
> **Contenido mínimo:** audiencia principal (ID de BI-BIC), decisión que atiende la pantalla y periodicidad de uso.

## 2. Catálogo de pantallas
> **Definición:** una fila por pantalla o informe.
> **Contenido mínimo por fila:** ID, nombre, audiencia, periodicidad, objetivo y decisión atendida.

| ID | Pantalla o informe | Audiencia | Periodicidad | Objetivo | Decisión (BI-BIC) |
|---|---|---|---|---|---|
| P-01 | | | | | D-01 |

## 3. KPI y visualizaciones por pantalla
> **Definición:** qué muestra cada pantalla y con qué visualización.
> **Contenido mínimo:** KPI o medida referenciada (ID), tipo de visualización y motivo de la elección según el tipo de pregunta (comparación, tendencia, composición o distribución).

| Pantalla | KPI o medida | Visualización | Motivo |
|---|---|---|---|
| P-01 | KPI-NNN | | |

## 4. Filtros y drill-down
> **Definición:** cómo se navega y se filtra cada pantalla.
> **Contenido mínimo:** filtros globales, filtros locales, niveles de drill-down y exportaciones permitidas, por pantalla.

## 5. Reglas de presentación
> **Definición:** convenciones que deben cumplir todas las visualizaciones.
> **Contenido mínimo:** unidades, redondeo, colores de umbral, tratamiento de datos faltantes y orden por defecto.

## 6. Control de acceso
> **Definición:** quién ve qué.
> **Contenido mínimo:** rol, restricción por fila o por entidad, columnas ocultas y justificación. Sin datos personales innecesarios.

| Rol | Pantallas | Restricción por fila | Columnas excluidas |
|---|---|---|---|
| | | | |

## 7. Pendientes
> **Contenido mínimo:** pantallas sin KPI definido, dependencias abiertas y responsable de cada una.

## 8. Validación
- [ ] Cada pantalla tiene audiencia y decisión enlazadas a BI-BIC
- [ ] Cada visualización referencia un KPI o medida del catálogo
- [ ] Cada filtro existe en el modelo DMD
- [ ] Control de acceso declarado por rol
- [ ] Ninguna métrica nueva fuera del catálogo
