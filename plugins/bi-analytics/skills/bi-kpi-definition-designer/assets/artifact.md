---
type: KPI
title: "KPI Definition — <nombre del KPI>"
description: "<una frase: qué mide el KPI y la decisión que soporta>"
id: BI-KPI-000
version: "1.0.0"
status: draft
classification: internal
owner: "<team:rol o human:nombre>"
product: "<producto o iniciativa>"
pack: bi-analytics
skill: bi-kpi-definition-designer
tags: [bi, analytics, kpi]
generated:
  by: bi-kpi-definition-designer/1.2.0
  at: "<ISO 8601 con zona>"
sources:
  - id: src-001
    resource: "<URI o ruta de la fuente>"
    title: "<título de la fuente>"
related: ["BI-BIC-000", "BI-CTLG-001"]
---
# KPI Definition — <nombre del KPI>

> **Definición:** especificación formal de un indicador. Un KPI por documento. Si dos KPI comparten fórmula, se documentan por separado y se enlazan.
> **Regla:** un KPI sin decisión de origen en el BIC queda como `gap` y no se aprueba.
> **Regla:** este documento es la única fuente de la definición del KPI. El catálogo `BI-CTLG-001` solo lo indexa (nombre, código, estado, versión).

## 1. Identificación
> **Definición:** nombre, código y objetivo del indicador.
> **Contenido mínimo:** nombre oficial, código `KPI-NNN`, objetivo en una frase y decisión de origen (ID de `BI-BIC`).

| Campo | Valor |
|---|---|
| Código | KPI-NNN |
| Nombre oficial | |
| Objetivo | |
| Decisión de origen | D-NN (BI-BIC-NNN) |
| Término de glosario | Enlace a TRM, o «Pendiente» |

## 2. Definición
> **Definición:** cómo se calcula el KPI, en lenguaje de negocio y en forma precisa.
> **Contenido mínimo:** fórmula en lenguaje de negocio, fórmula formal, unidad, grano temporal y geográfico, dimensiones de corte y filtros obligatorios.

- **Fórmula de negocio:**
- **Fórmula formal:**
- **Unidad:**
- **Grano temporal:**
- **Grano geográfico o de entidad:**
- **Dimensiones de corte:**
- **Filtros obligatorios:**

## 3. Gobierno
> **Definición:** quién responde por el KPI y cómo se evalúa.
> **Contenido mínimo:** owner, frecuencia de actualización y umbrales o metas. Un umbral sin fuente documentada se marca «Pendiente».

| Campo | Valor |
|---|---|
| Owner | |
| Frecuencia de actualización | |
| Umbral o meta | Pendiente o fuente |
| Sentido de mejora | ↑ / ↓ |

## 4. Casos límite
> **Definición:** situaciones en las que el cálculo es ambiguo o no aplica.
> **Contenido mínimo:** al menos división por cero, datos tardíos y periodos parciales, con la regla acordada para cada uno.

| Caso | Regla de cálculo | Fuente |
|---|---|---|
| División por cero | | |
| Datos tardíos | | |
| Periodo parcial | | |

## 5. Cambios y versiones
> **Definición:** historial de cambios de fórmula o grano.
> **Contenido mínimo:** versión, fecha, cambio y motivo. Un cambio de fórmula o grano exige nueva versión del documento.

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| 1.0.0 | | Creación | |

## 6. Trazabilidad
> **Definición:** vínculos del KPI con el resto de la línea base.
> **Contenido mínimo:** decisión de BIC, términos de glosario, medidas del DMD y pantallas del DSH que lo usan (IDs). Si aún no existen, «Pendiente».

## 7. Limitaciones y pendientes
> **Definición:** lo que el KPI no mide y qué falta para aprobarlo.
> **Contenido mínimo:** lista con responsable.

## 8. Validación
- [ ] Fórmula de negocio y formal coinciden
- [ ] Owner, grano y unidad completos
- [ ] Decisión de origen enlazada a BI-BIC
- [ ] Casos límite con regla de cálculo
- [ ] Umbrales con fuente o marcados «Pendiente»
